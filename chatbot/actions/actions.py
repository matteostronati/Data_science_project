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
import pandas as pd
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

df = pd.read_csv(r"C:\Users\matte\Desktop\Data_science_project\chatbot\dataset\goodreads_chatbot_cleaned.csv")

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
        
        # Parti dal dataset completo
        filtered_df = df.copy()
        
        # Applica filtri uno per uno
        try:
            # Filtro per genere
            if genre:
                filtered_df = filtered_df[
                    filtered_df['genres'].str.contains(genre, case=False, na=False)
                ]
            
            # Filtro per titolo (se cercano titolo specifico, restituisci solo quello)
            if title:
                filtered_df = filtered_df[
                    filtered_df['title'].str.contains(title, case=False, na=False)
                ]
                # Per titolo, restituisci solo 1 risultato
                return self._return_single_book(filtered_df, dispatcher, title)
            
            # Filtro per autore
            if author:
                filtered_df = filtered_df[
                    filtered_df['author'].str.contains(author, case=False, na=False)
                ]
            
            # Filtro per numero esatto di pagine (±50 pagine)
            if num_pages:
                target_pages = float(num_pages)
                filtered_df = filtered_df.dropna(subset=['num_pages'])
                filtered_df = filtered_df[
                    (filtered_df['num_pages'] >= target_pages - 50) &
                    (filtered_df['num_pages'] <= target_pages + 50)
                ]
            
            # Filtro per min pagine
            if min_pages:
                filtered_df = filtered_df.dropna(subset=['num_pages'])
                filtered_df = filtered_df[filtered_df['num_pages'] >= float(min_pages)]
            
            # Filtro per max pagine
            if max_pages:
                filtered_df = filtered_df.dropna(subset=['num_pages'])
                filtered_df = filtered_df[filtered_df['num_pages'] <= float(max_pages)]
            
            # Filtro per rating esatto (±0.2)
            if avg_rating:
                target_rating = float(avg_rating)
                filtered_df = filtered_df.dropna(subset=['avg_rating'])
                filtered_df = filtered_df[
                    (filtered_df['avg_rating'] >= target_rating - 0.2) &
                    (filtered_df['avg_rating'] <= target_rating + 0.2)
                ]
            
            # Filtro per min rating
            if min_rating:
                filtered_df = filtered_df.dropna(subset=['avg_rating'])
                filtered_df = filtered_df[filtered_df['avg_rating'] >= float(min_rating)]
            
            # Filtro per max rating
            if max_rating:
                filtered_df = filtered_df.dropna(subset=['avg_rating'])
                filtered_df = filtered_df[filtered_df['avg_rating'] <= float(max_rating)]
            
            # Filtro per personaggio
            if characters:
                filtered_df = filtered_df[
                    filtered_df['characters'].str.contains(characters, case=False, na=False)
                ]
            
            # Verifica se ci sono risultati
            if filtered_df.empty:
                active_filters = self._get_active_filters(
                    genre, title, author, num_pages, min_pages, max_pages,
                    avg_rating, min_rating, max_rating, characters
                )
                dispatcher.utter_message(
                    text=f"Sorry, I couldn't find any books matching your criteria: {active_filters}.\n\nYou can type \"new search\" to start fresh and clear all filters. "
                
                )
                return []
            
            # Ordina per numero di recensioni (più popolari prima)
            filtered_df = filtered_df.sort_values(
                ['num_ratings', 'avg_rating'], 
                ascending=[False, False]
            )
            
            # Prendi i top 3-5 libri (3 se ci sono pochi risultati, 5 altrimenti)
            num_results = min(5 if len(filtered_df) >= 5 else 3, len(filtered_df))
            top_books = filtered_df.head(num_results)
            
            # Costruisci il messaggio testuale (come prima)
            message = self._format_multiple_books_message(
                top_books, genre, author, min_pages, max_pages, min_rating, characters
            )
            
            # Genera i bottoni con solo l'indice
            buttons = []
            for idx, (_, book) in enumerate(top_books.iterrows(), 1):
                # Tronca il titolo per il display
                display_title = book['title']
                if len(display_title) > 50:
                    display_title = display_title[:50] + "..."
                
                button = {
                    "title": f"{idx}. {display_title}",
                    "payload": f"/select_book_{idx}"
                }
                buttons.append(button)
            
            # Invia messaggio con i bottoni
            dispatcher.utter_message(
                text=message, 
                buttons=buttons,
                button_type="vertical"  
            )
            
            # Salva i libri nello slot per recuperarli dopo
            return [SlotSet("suggested_books", top_books.to_dict('records'))]

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {str(e)}")
        return []
        
    
    def _return_single_book(self, filtered_df, dispatcher, title):
        """Helper per restituire un singolo libro quando cercano per titolo"""
        if filtered_df.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a book titled '{title}'.\nYou can always type \"new search\" to start fresh and clear all filters.")
            return []
        
        # Ordina per num_ratings per prendere la versione più popolare
        book = filtered_df.sort_values('num_ratings', ascending=False).iloc[0]
        message = self._format_single_book_detail(book)
        dispatcher.utter_message(text=message)
        
        # Imposta lo slot per indicare che abbiamo trovato un libro specifico
        return [SlotSet("found_specific_book", True)]
    
    def _format_multiple_books_message(self, books_df, genre, author, min_pages, max_pages, min_rating, characters):
        """Formatta messaggio con 3-5 libri suggeriti"""
        # Header con criteri attivi
        active_criteria = []
        if genre:
            active_criteria.append(f"{genre} genre")
        if author:
            active_criteria.append(f"by the author {author}")
            #Aggiungere il caso in cui si mette il numero specifico di pagine
        if min_pages or max_pages:
            if min_pages and max_pages:
                active_criteria.append(f"with {int(min_pages)}-{int(max_pages)} pages")
            elif min_pages:
                active_criteria.append(f"over {int(min_pages)} pages")
            elif max_pages:
                active_criteria.append(f"under {int(max_pages)} pages")
        if min_rating:
            active_criteria.append(f"rating ≥ {min_rating}")
        if characters:
            active_criteria.append(f"with characters {characters}")
        
        criteria_text = " ".join(active_criteria) if active_criteria else "all books"
        
        message = f"Here are {len(books_df)} great books {criteria_text}:\n\n"
        
        # Lista i libri
        for idx, (_, book) in enumerate(books_df.iterrows(), 1):
            message += f"{idx}. 📖 {book['title']}\n"
            message += f"     ✍️ Author: {book['author']}\n"
            
            if pd.notna(book['avg_rating']):
                stars = "⭐" * int(round(book['avg_rating']))
                message += f"     {book['avg_rating']:.2f}/5.0 {stars}"
            
            if pd.notna(book['num_ratings']):
                message += f" ({int(book['num_ratings']):,} ratings)"
            
            if pd.notna(book['num_pages']):
                message += f"\n     {int(book['num_pages'])} pages"
            
            message += "\n\n"
        
        # Suggerimento per affinare la ricerca
        message += "✨ Refine your search:\n"
        suggestions = []
        if not genre:
            suggestions.append("• Specify a genre 🎨")
        if not author:
            suggestions.append("• Specify an author ✍️")
        if not (min_pages or max_pages):
            suggestions.append("• Add page count preferences 🔢")
        if not min_rating:
            suggestions.append("• Filter by minimum rating 📈")
        if not characters:
            suggestions.append("• Search by character name 👤")
        
        if suggestions:
            message += "\n".join(suggestions[:3])  # Max 3 suggerimenti
        else:
            message += "You've applied many filters! Would you like details on any of these books?"

        message += "\n\n🔍 Click a button below to see full details about the book!"
        message += "\n🔄 You can always type \"new search\" to start fresh and clear all filters."
        return message
    
    def _format_single_book_detail(self, book):
        """Formatta dettagli completi di un singolo libro"""
        message = f"📖 {book['title']}\n"
        message += f"✍️ Author: {book['author']}\n"
        
        # Rating
        if pd.notna(book['avg_rating']):
            stars = "⭐" * int(round(book['avg_rating']))
            message += f"📈 Rating: {book['avg_rating']:.2f}/5.0 {stars}\n"
        
        # Numero recensioni
        if pd.notna(book['num_ratings']):
            message += f"📝 Reviews: {int(book['num_ratings']):,} ratings\n"
        
        # Pagine
        if pd.notna(book['num_pages']):
            message += f"🔢 Number of pages: {int(book['num_pages'])}\n"
        
        # Anno pubblicazione
        if pd.notna(book['year']):
            message += f"🗓️ Published in the year: {int(book['year'])}\n"
        
        # Generi
        if pd.notna(book['genres']):
            genres_list = book['genres'].split(',')[:5]
            message += f"🎨 Genres: {', '.join(genres_list)}\n"
        
        # Descrizione
        if pd.notna(book['description']):
            desc = book['description'][:500]
            if len(book['description']) > 500:
                desc += "..."
            message += f"ℹ️ Description:\n{desc}"
        
        return message
    
    def _get_active_filters(self, genre, title, author, num_pages, min_pages, 
                           max_pages, avg_rating, min_rating, max_rating, characters):
        """Helper per costruire stringa con filtri attivi"""
        active = []
        if genre:
            active.append(f"genre={genre}")
        if title:
            active.append(f"title={title}")
        if author:
            active.append(f"author={author}")
        if num_pages:
            active.append(f"pages~{num_pages}")
        if min_pages:
            active.append(f"min_pages={min_pages}")
        if max_pages:
            active.append(f"max_pages={max_pages}")
        if avg_rating:
            active.append(f"rating~{avg_rating}")
        if min_rating:
            active.append(f"min_rating={min_rating}")
        if max_rating:
            active.append(f"max_rating={max_rating}")
        if characters:
            active.append(f"character={characters}")
        return ", ".join(active) if active else "none"

class ActionResetSlots(Action):
    """Reset tutti gli slots SENZA messaggio (silente)"""
    
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
            SlotSet("found_specific_book", False),
            SlotSet("suggested_books", None), 
            SlotSet("book_index", None), 
        ]


class ActionResetSlotsWithMessage(Action):
    """Reset tutti gli slots CON messaggio (quando l'utente chiede nuova ricerca)"""
    
    def name(self) -> Text:
        return "action_reset_slots_with_message"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Starting a fresh search! What are you looking for?")
        
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
            SlotSet("found_specific_book", False),
            SlotSet("suggested_books", None), 
            SlotSet("book_index", None), 
        ]

class ActionShowSelectedBook(Action):
    """Mostra i dettagli del libro selezionato dall'utente"""
    
    def name(self) -> Text:
        return "action_show_selected_book"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Recupera l'indice del libro selezionato dall'utente
        book_index = tracker.get_slot("book_index")
        
        # Se non c'è, estrailo dal messaggio
        if not book_index:
            import re
            last_message = tracker.latest_message.get('text', '')
            match = re.search(r'(\d+)', last_message)  # Estrae qualsiasi numero
            if match:
                book_index = match.group(1)

        # Recupera la lista dei libri salvata in precedenza
        suggested_books = tracker.get_slot("suggested_books")
        
        # Controllo di sicurezza
        if not book_index or not suggested_books:
            dispatcher.utter_message(
                text="Sorry, I couldn't find that book. Please search again."
            )
            return []
        
        try:
            # Converti l'indice a numero (1-based → 0-based)
            idx = int(book_index) - 1
            
            # Validazione indice
            if idx < 0 or idx >= len(suggested_books):
                dispatcher.utter_message(
                    text=f"Invalid selection. Please choose a number between 1 and {len(suggested_books)}."
                )
                return []
            
            # Prendi il libro dalla lista salvata
            selected_book = suggested_books[idx]
            
            # Converti dict → pandas Series (per compatibilità con la funzione esistente)
            book_series = pd.Series(selected_book)
            
            # Formatta e invia i dettagli completi
            message = self._format_single_book_detail(book_series)
            dispatcher.utter_message(text=message)
            
            # Imposta che abbiamo trovato un libro specifico (per il flow)
            return [SlotSet("found_specific_book", True)]
            
        except (ValueError, KeyError, IndexError) as e:
            dispatcher.utter_message(
                text=f"Sorry, there was an error selecting that book: {str(e)}"
            )
            return []
    
    def _format_single_book_detail(self, book):
        """Formatta dettagli completi di un singolo libro"""
        message = f"📖 {book['title']}\n"
        message += f"✍️ Author: {book['author']}\n"
        
        # Rating
        if pd.notna(book['avg_rating']):
            stars = "⭐" * int(round(book['avg_rating']))
            message += f"📈 Rating: {book['avg_rating']:.2f}/5.0 {stars}\n"
        
        # Numero recensioni
        if pd.notna(book['num_ratings']):
            message += f"📝 Reviews: {int(book['num_ratings']):,} ratings\n"
        
        # Pagine
        if pd.notna(book['num_pages']):
            message += f"🔢 Number of pages: {int(book['num_pages'])}\n"
        
        # Anno pubblicazione
        if pd.notna(book['year']):
            message += f"🗓️ Published in the year: {int(book['year'])}\n"
        
        # Generi
        if pd.notna(book['genres']):
            genres_list = book['genres'].split(',')[:5]
            message += f"🎨 Genres: {', '.join(genres_list)}\n"
        
        # Descrizione
        if pd.notna(book['description']):
            desc = book['description'][:500]
            if len(book['description']) > 500:
                desc += "..."
            message += f"ℹ️ Description:\n{desc}"
        
        return message

class ActionDefaultFallback(Action):
    """Fallback quando il bot non capisce"""
    
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Invia uno dei messaggi di utter_default
        dispatcher.utter_message(response="utter_default")
        
        # Annulla l'ultimo messaggio utente per non confondere il tracker
        return [UserUtteranceReverted()]