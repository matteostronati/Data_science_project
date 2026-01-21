# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ActionSearchBooks(Action):
    """Action unica che cerca libri combinando tutti i criteri disponibili"""
    
    def name(self) -> Text:
        return "action_search_books"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Estrai tutti gli slots
        genre = tracker.get_slot("genre")
        title = tracker.get_slot("title")
        author = tracker.get_slot("author")
        num_pages = tracker.get_slot("num_pages")
        min_pages = tracker.get_slot("min_num_pages")
        max_pages = tracker.get_slot("max_num_pages")
        avg_rating = tracker.get_slot("avg_rating")
        min_rating = tracker.get_slot("min_avg_rating")
        max_rating = tracker.get_slot("max_avg_rating")
        characters = tracker.get_slot("characters")
        
        # Costruisci messaggio debug con criteri attivi
        active_filters = []
        if genre:
            active_filters.append(f"Genre: {genre}")
        if title:
            active_filters.append(f"Title: {title}")
        if author:
            active_filters.append(f"Author: {author}")
        if num_pages:
            active_filters.append(f"Pages: ~{num_pages}")
        if min_pages:
            active_filters.append(f"Min pages: {min_pages}")
        if max_pages:
            active_filters.append(f"Max pages: {max_pages}")
        if avg_rating:
            active_filters.append(f"Rating: ~{avg_rating}")
        if min_rating:
            active_filters.append(f"Min rating: {min_rating}")
        if max_rating:
            active_filters.append(f"Max rating: {max_rating}")
        if characters:
            active_filters.append(f"Character: {characters}")
        
        if active_filters:
            filters_text = ", ".join(active_filters)
            message = f"[DEBUG] Searching with filters: {filters_text}"
        else:
            message = "[DEBUG] No filters specified - would ask for more info"
        
        dispatcher.utter_message(text=message)
        return []


class ActionResetSlots(Action):
    """Reset tutti gli slots per una nuova ricerca"""
    
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [
            SlotSet("genre", None),
            SlotSet("title", None),
            SlotSet("author", None),
            SlotSet("num_pages", None),
            SlotSet("min_num_pages", None),
            SlotSet("max_num_pages", None),
            SlotSet("avg_rating", None),
            SlotSet("min_avg_rating", None),
            SlotSet("max_avg_rating", None),
            SlotSet("characters", None),
        ]
