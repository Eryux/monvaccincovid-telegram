import settings
import json
import re

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Unauthorized
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler

from models import CenterModel, ChannelModel
from doctolib import DoctolibRequest, DoctolibUtils

# -----------------------------------------------

def command_start(update, context):
    update.message.reply_text("Bienvenue, ajouter des centres de vaccination avec la commande /check pour commencer à utiliser MonVaccinCovid.")
    return ConversationHandler.END


def command_check_start(update, context):
    channel_id = str(update.effective_chat.id)

    update.message.reply_text("Envoyez moi les liens Doctolib des centres de vaccination à surveiller (un à la fois)\n\n"
        + "Exemple : https://www.doctolib.fr/centre-de-sante/paris/centre-de-vaccination-covid-19-ville-de-paris?pid=practice-166459\n\n"
        + "Pour trouver les centres de vaccination proche de chez vous, lancer une recherche sur le site Doctolib : https://www.doctolib.fr/vaccination-covid-19/paris", disable_web_page_preview=True, reply_markup=ReplyKeyboardMarkup([['/fin']]))

    return 0

def command_check_confirm(update, context):
    channel_id = str(update.effective_chat.id)

    # Verify center limit
    if ChannelModel.select().where(ChannelModel.channel == channel_id).count() > settings.WATCH_LIMIT:
        update.message.reply_text("Désolé, vous avez atteint la limite de centres de vaccinations que vous pouvez surveiller.")
        return ConversationHandler.END

    # Get center data
    api = DoctolibRequest()

    center_data = {}

    try:
        center_data = api.get_booking(update.message.text)
    except:
        update.message.reply_text("Désolé, assurez-vous que le lien est bien valide. (0)")
        return 0

    if len(center_data) == 0:
        update.message.reply_text("Désolé, assurez-vous que le lien est bien valide. (4)")
        return 0

    # Parse URL
    center_url_data = DoctolibUtils.parse_center_url(update.message.text)

    # Get center place
    try:
        center_place = None
        if center_url_data['practice'] != -1:
            practice_name = "practice-" + str(center_url_data['practice'])

            center_place = DoctolibUtils.place_from_center(center_data, practice_name)

            if center_place is None:
                update.message.reply_text("Désolé, assurez-vous que le lien est bien valide. (1)")
                return 0
        else:
            center_place = center_data['data']['places'][0]
    except:
        update.message.reply_text("Désolé, assurez-vous que le lien est bien valide. (2)")
        return 0

    # Check if online booking is available
    try:
        has_booking = False

        center_motives = DoctolibUtils.motives_from_center(center_data, settings.DOCTOLIB_REFS)
        
        for motive in center_motives:
            center_agendas = DoctolibUtils.agendas_from_center(center_data, motive['id'], center_place['practice_ids'][0], True)
            if len(center_agendas) > 0:
                has_booking = True
                break

        if has_booking is False:
            update.message.reply_text("Désolé, ce centre ne propose pas de réservation.")
            return 0
    except:
        update.message.reply_text("Désolé, assurez-vous que le lien est bien valide. (3)")
        return 0

    # Get or add center
    center = None

    try:
        center = CenterModel.get(CenterModel.doctolib_id == center_data['data']['profile']['id'], CenterModel.doctolib_practice == center_place['practice_ids'][0])
    except:
        center = CenterModel()
        center.name = center_data['data']['profile']['name_with_title']
        center.doctolib_id = center_data['data']['profile']['id']
        center.doctolib_name = center_url_data['name']
        center.doctolib_url = center_url_data['clear_url']
        center.doctolib_practice = center_place['practice_ids'][0]
        center.doctolib_data = json.dumps(center_data)
        center.city = center_place['city']
        center.zip_code = center_place['zipcode']
        center.address = center_place['address']
        center.latitude = center_place['latitude']
        center.longitude = center_place['longitude']
        center.place_name = center_place['formal_name']
        center.save()

    # Add center to channel
    if ChannelModel.select().where(ChannelModel.center == center, ChannelModel.channel == channel_id).count() > 0:
        update.message.reply_text("Je surveille déjà ce centre de vaccination.")
    else:
        ChannelModel.create(center = center, channel = channel_id)
        update.message.reply_text("Centre de vaccination ajouté.")

    return 0

def command_check_end(update, context):
    update.message.reply_text("Ajout des centres de vaccination terminé.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# -----------------------------------------------

def command_list(update, context):
    data = ChannelModel.select().join(CenterModel).where(ChannelModel.channel == str(update.effective_chat.id))

    if len(data) > 0:
        message = "Je surveille {} centre(s) de vaccination :\n".format(len(data))
        for x in data:
            message += "\nn° {} - {} [{}]".format(x.center_id, x.center.name, x.center.doctolib_practice)
        update.message.reply_text(message)
    else:
        update.message.reply_text("Aucun centre de vaccination sous surveillance.\nAjouter en avec la commande /check")

    return ConversationHandler.END

# -----------------------------------------------

def command_stop_start(update, context):
    data = ChannelModel.select().join(CenterModel).where(ChannelModel.channel == str(update.effective_chat.id))

    if len(data) > 0:
        message = "Je surveille {} centre(s) de vaccination :\n".format(len(data))
        for x in data:
            message += "\nn° {} - {} [{}]".format(x.center_id, x.center.name, x.center.doctolib_practice)
        message += "\n\nDonnez moi le numéro du centre de vaccination à ne plus surveiller ou envoyer /annuler"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Aucun centre de vaccination sous surveillance.\nAjouter en avec la commande /check")
        return ConversationHandler.END

    return 0

def command_stop(update, context):
    channel_id = str(update.effective_chat.id)
    try:
        channel = ChannelModel.get(ChannelModel.channel == channel_id, ChannelModel.center == int(update.message.text))
        channel.delete_instance()
        update.message.reply_text("Le centre de vaccination : {}, n'est plus surveillé.".format(channel.center.name))
    except:
        update.message.reply_text("Le numéro donné n'est pas valide.")
    return ConversationHandler.END

# -----------------------------------------------

def command_stopall_start(update, context):
    update.message.reply_text("Êtes-vous sûr de vouloir arreter la surveillance ?\nRéponder par oui ou non",
        reply_markup=ReplyKeyboardMarkup([['oui', 'non']], one_time_keyboard = True))
    return 0

def command_stopall(update, context):
    if update.message.text.lower() == "oui":
        ChannelModel.delete().where(ChannelModel.channel == str(update.effective_chat.id)).execute()
        update.message.reply_text("Voilà, je ne surveille plus de centre de vaccination pour vous.")
    return ConversationHandler.END

# -----------------------------------------------

def cancel(update, context):
    update.message.reply_text("Abandon.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def action(update, context):
    query = update.callback_query
    query.answer()

    path = query.data.split('/')

    if len(path) == 3 and path[0] == 'center' and path[1] == 'location':
        center_id = int(path[2])

        try:
            center = CenterModel.get(CenterModel.id == center_id)
            query.message.reply_location(center.latitude, center.longitude)
            query.message.reply_text("{}\n{}\n{} {}".format(center.place_name, center.address, center.zip_code, center.city))
        except:
            pass

# -----------------------------------------------

class TelegramClient:

    def __init__(self):
        self.updater = Updater(token=settings.TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', command_start))

        self.dispatcher.add_handler(ConversationHandler(
            entry_points = [CommandHandler('check', command_check_start)],
            states = {
                0: [MessageHandler(Filters.regex('^https://www\.doctolib\.fr/.+'), command_check_confirm)]
            },
            fallbacks = [CommandHandler('fin', command_check_end)]
        ))

        self.dispatcher.add_handler(CommandHandler('liste', command_list))

        self.dispatcher.add_handler(CallbackQueryHandler(action))

        self.dispatcher.add_handler(ConversationHandler(
            entry_points = [CommandHandler('stop', command_stop_start)],
            states = {
                0: [MessageHandler(Filters.regex('^[0-9]+$'), command_stop)]
            },
            fallbacks = [CommandHandler('annuler', cancel)]
        ))

        self.dispatcher.add_handler(ConversationHandler(
            entry_points = [CommandHandler('stopall', command_stopall_start)],
            states = {
                0: [MessageHandler(Filters.regex('^([Oo]ui)|([Nn]on)$'), command_stopall)]
            },
            fallbacks = [CommandHandler('annuler', cancel)]
        ))


    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    
    def stop(self):
        if self.updater is not None:
            self.updater.stop()
        self.updater = None

    
    def send_message(self, channel_id, message):
        try:
            chat = self.updater.bot.get_chat(channel_id)
            self.updater.bot.send_message(chat.id, message, disable_web_page_preview=False)
        except Unauthorized:
            pass
        except:
            pass


    def send_alert_message(self, channel_id, message, center_id):
        chat = self.updater.bot.get_chat(channel_id)
        keyboard = [[InlineKeyboardButton("Voir la localisation", callback_data='center/location/{}'.format(center_id))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.updater.bot.send_message(chat.id, message, reply_markup=reply_markup, disable_web_page_preview=False)

# End of file bot.py