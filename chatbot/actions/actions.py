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
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ActionRecommendBook(Action):
    
    def name(self) -> Text:
        return "action_recommend_book"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionRecommendBook called - would recommend a book by genre")
        return []


class ActionFindByTitle(Action):
    
    def name(self) -> Text:
        return "action_find_by_title"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByTitle called - would find book by title")
        return []


class ActionFindByAuthor(Action):
    
    def name(self) -> Text:
        return "action_find_by_author"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByAuthor called - would find books by author")
        return []


class ActionFindByPageRange(Action):
    
    def name(self) -> Text:
        return "action_find_by_page_range"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByPageRange called - would find books by page range")
        return []


class ActionFindByPage(Action):
    
    def name(self) -> Text:
        return "action_find_by_page"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByPage called - would find books by approximate pages")
        return []


class ActionFindByAuthorAndPages(Action):
    
    def name(self) -> Text:
        return "action_find_by_author_and_pages"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByAuthorAndPages called - would find books by author and pages")
        return []


class ActionFindByRating(Action):
    
    def name(self) -> Text:
        return "action_find_by_rating"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByRating called - would find books by rating")
        return []


class ActionFindByCharacter(Action):
    
    def name(self) -> Text:
        return "action_find_by_character"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="[DEBUG] ActionFindByCharacter called - would find books by character")
        return []
