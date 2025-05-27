"""
Модуль для генерации случайных данных пользователей с поддержкой разных стран.
"""
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from .password_generator import generate_password

logger = logging.getLogger(__name__)

class UserGenerator:
    # Общие данные для всех стран
    _occupations = {
        "RU": [
            "Программист", "Врач", "Учитель", "Инженер", "Дизайнер", "Менеджер", "Бухгалтер", 
            "Юрист", "Архитектор", "Маркетолог", "Психолог", "Журналист", "Фотограф", 
            "Системный администратор", "Аналитик данных", "Финансовый консультант", 
            "Переводчик", "Копирайтер", "HR-специалист", "Продакт-менеджер", "Тестировщик",
            "Научный сотрудник", "Преподаватель", "Фармацевт", "Стоматолог", "Ветеринар",
            "Риэлтор", "Логист", "SMM-специалист", "Бизнес-аналитик"
        ],
        "US": [
            "Software Engineer", "Doctor", "Teacher", "Engineer", "Designer", "Manager", 
            "Accountant", "Lawyer", "Architect", "Marketing Specialist", "Data Scientist",
            "Product Manager", "UX Designer", "Business Analyst", "Financial Advisor",
            "Sales Representative", "HR Manager", "System Administrator", "DevOps Engineer",
            "Content Writer", "Digital Marketing Manager", "Research Scientist", "Professor",
            "Pharmacist", "Dentist", "Veterinarian", "Real Estate Agent", "Logistics Manager",
            "Social Media Manager", "Business Consultant"
        ],
        "GB": [
            "Software Developer", "Physician", "Teacher", "Engineer", "Designer", "Manager",
            "Accountant", "Solicitor", "Architect", "Marketing Manager", "Data Analyst",
            "Project Manager", "UI Designer", "Systems Analyst", "Investment Advisor",
            "Sales Executive", "HR Consultant", "IT Support", "Cloud Engineer",
            "Technical Writer", "Digital Strategist", "Research Fellow", "Lecturer",
            "Clinical Pharmacist", "Dental Surgeon", "Veterinary Surgeon", "Estate Agent",
            "Supply Chain Manager", "Digital Marketing Executive", "Management Consultant"
        ],
        "DE": [
            "Softwareentwickler", "Arzt", "Lehrer", "Ingenieur", "Designer", "Manager",
            "Buchhalter", "Rechtsanwalt", "Architekt", "Marketingmanager", "Datenwissenschaftler",
            "Projektleiter", "UX-Designer", "Geschäftsanalyst", "Finanzberater",
            "Vertriebsleiter", "Personalreferent", "Systemadministrator", "DevOps-Ingenieur",
            "Texter", "Online-Marketing-Manager", "Wissenschaftler", "Professor",
            "Apotheker", "Zahnarzt", "Tierarzt", "Immobilienmakler", "Logistikmanager",
            "Social-Media-Manager", "Unternehmensberater"
        ],
        "FR": [
            "Développeur", "Médecin", "Professeur", "Ingénieur", "Designer", "Manager",
            "Comptable", "Avocat", "Architecte", "Responsable Marketing", "Data Scientist",
            "Chef de Projet", "Designer UX", "Analyste d'Affaires", "Conseiller Financier",
            "Commercial", "Responsable RH", "Administrateur Système", "Ingénieur DevOps",
            "Rédacteur", "Responsable Marketing Digital", "Chercheur", "Professeur",
            "Pharmacien", "Dentiste", "Vétérinaire", "Agent Immobilier", "Responsable Logistique",
            "Community Manager", "Consultant en Management"
        ]
    }

    _education_levels = {
        "RU": [
            "Среднее образование", "Среднее специальное образование", "Бакалавр",
            "Магистр", "Кандидат наук", "Доктор наук", "Профессиональная переподготовка",
            "MBA", "Специалист", "Незаконченное высшее", "Аспирантура"
        ],
        "US": [
            "High School Diploma", "Associate's Degree", "Bachelor's Degree",
            "Master's Degree", "Ph.D.", "Professional Degree", "Vocational Training",
            "MBA", "Post-Graduate Certificate", "Some College", "Doctoral Candidate"
        ],
        "GB": [
            "GCSE", "A-Levels", "Bachelor's Degree", "Master's Degree", "Ph.D.",
            "Professional Qualification", "HND", "Foundation Degree", "BTEC",
            "Higher Apprenticeship", "Postgraduate Diploma"
        ],
        "DE": [
            "Hauptschulabschluss", "Realschulabschluss", "Abitur", "Bachelor",
            "Master", "Promotion", "Ausbildung", "Diplom", "Staatsexamen",
            "Meister", "Fachwirt"
        ],
        "FR": [
            "Baccalauréat", "BTS/DUT", "Licence", "Master", "Doctorat",
            "Grande École", "CAP", "BEP", "DEUG", "Licence Professionnelle",
            "Diplôme d'Ingénieur"
        ]
    }

    _universities = {
        "RU": [
            "МГУ", "СПбГУ", "МФТИ", "МГТУ им. Баумана", "НГУ",
            "ВШЭ", "ИТМО", "РАНХиГС", "РУДН", "УрФУ"
        ],
        "US": [
            "Harvard University", "MIT", "Stanford University", "Yale University",
            "Columbia University", "Princeton University", "UC Berkeley",
            "University of Chicago", "CalTech", "UCLA"
        ],
        "GB": [
            "University of Oxford", "University of Cambridge", "Imperial College London",
            "UCL", "University of Edinburgh", "King's College London",
            "University of Manchester", "LSE", "University of Bristol",
            "University of Warwick"
        ],
        "DE": [
            "Technische Universität München", "Ludwig-Maximilians-Universität München",
            "Humboldt-Universität zu Berlin", "Freie Universität Berlin",
            "Universität Heidelberg", "RWTH Aachen", "Universität Hamburg",
            "Technische Universität Berlin", "Universität Frankfurt",
            "Universität Köln"
        ],
        "FR": [
            "Sorbonne Université", "École Polytechnique", "Sciences Po",
            "École Normale Supérieure", "HEC Paris", "ESSEC",
            "Université Paris-Saclay", "CentraleSupélec",
            "École des Ponts ParisTech", "INSEAD"
        ]
    }

    _languages = {
        "RU": [
            "Русский", "Английский", "Немецкий", "Французский", "Испанский", "Китайский",
            "Японский", "Итальянский", "Португальский", "Корейский", "Арабский",
            "Турецкий", "Польский", "Чешский", "Шведский", "Финский", "Норвежский",
            "Греческий", "Иврит", "Хинди"
        ],
        "US": [
            "English", "Spanish", "French", "German", "Chinese", "Japanese",
            "Italian", "Portuguese", "Korean", "Arabic", "Russian", "Turkish",
            "Polish", "Czech", "Swedish", "Finnish", "Norwegian", "Greek",
            "Hebrew", "Hindi"
        ],
        "GB": [
            "English", "French", "German", "Spanish", "Italian", "Arabic",
            "Chinese", "Japanese", "Portuguese", "Russian", "Polish", "Turkish",
            "Hindi", "Bengali", "Urdu", "Punjabi", "Welsh", "Gaelic",
            "Greek", "Dutch"
        ],
        "DE": [
            "Deutsch", "Englisch", "Französisch", "Spanisch", "Italienisch", "Russisch",
            "Türkisch", "Arabisch", "Chinesisch", "Japanisch", "Portugiesisch", "Polnisch",
            "Niederländisch", "Schwedisch", "Tschechisch", "Griechisch", "Koreanisch",
            "Ungarisch", "Rumänisch", "Kroatisch"
        ],
        "FR": [
            "Français", "Anglais", "Allemand", "Espagnol", "Italien", "Arabe",
            "Chinois", "Japonais", "Portugais", "Russe", "Néerlandais", "Turc",
            "Polonais", "Grec", "Suédois", "Coréen", "Hindi", "Vietnamien",
            "Roumain", "Hongrois"
        ]
    }

    _hobbies = {
        "RU": [
            "Чтение", "Путешествия", "Фотография", "Спорт", "Музыка", "Кулинария", 
            "Рисование", "Йога", "Танцы", "Садоводство", "Программирование", "Шахматы",
            "Рыбалка", "Охота", "Велоспорт", "Бег", "Плавание", "Скалолазание",
            "Настольные игры", "Коллекционирование", "Рукоделие", "Медитация",
            "Волонтерство", "Блоггинг", "Фитнес", "Походы", "Серфинг", "Сноуборд",
            "Гитара", "Фортепиано", "Вокал", "Театр", "Кино", "Аниме", "Косплей"
        ],
        "US": [
            "Reading", "Traveling", "Photography", "Sports", "Music", "Cooking",
            "Painting", "Yoga", "Dancing", "Gardening", "Coding", "Chess",
            "Fishing", "Hunting", "Cycling", "Running", "Swimming", "Rock Climbing",
            "Board Games", "Collecting", "Crafting", "Meditation",
            "Volunteering", "Blogging", "Fitness", "Hiking", "Surfing", "Snowboarding",
            "Guitar", "Piano", "Singing", "Theater", "Movies", "Anime", "Cosplay"
        ],
        "GB": [
            "Reading", "Travelling", "Photography", "Sports", "Music", "Cooking",
            "Painting", "Yoga", "Dancing", "Gardening", "Cricket", "Football",
            "Rugby", "Tennis", "Golf", "Running", "Swimming", "Climbing",
            "Board Games", "Collecting", "Crafting", "Meditation",
            "Volunteering", "Blogging", "Fitness", "Hiking", "Surfing", "Cycling",
            "Guitar", "Piano", "Singing", "Theatre", "Cinema", "Gaming", "DIY"
        ],
        "DE": [
            "Lesen", "Reisen", "Fotografie", "Sport", "Musik", "Kochen",
            "Malen", "Yoga", "Tanzen", "Gartenarbeit", "Programmierung", "Schach",
            "Angeln", "Wandern", "Radfahren", "Laufen", "Schwimmen", "Klettern",
            "Brettspiele", "Sammeln", "Basteln", "Meditation",
            "Freiwilligenarbeit", "Bloggen", "Fitness", "Bergsteigen", "Surfen", "Skifahren",
            "Gitarre", "Klavier", "Gesang", "Theater", "Kino", "Gaming", "Heimwerken"
        ],
        "FR": [
            "Lecture", "Voyages", "Photographie", "Sport", "Musique", "Cuisine",
            "Peinture", "Yoga", "Danse", "Jardinage", "Programmation", "Échecs",
            "Pêche", "Randonnée", "Cyclisme", "Course", "Natation", "Escalade",
            "Jeux de société", "Collection", "Bricolage", "Méditation",
            "Bénévolat", "Blogging", "Fitness", "Alpinisme", "Surf", "Ski",
            "Guitare", "Piano", "Chant", "Théâtre", "Cinéma", "Jeux vidéo", "DIY"
        ]
    }

    _blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    _marital_status = {
        "RU": ["Не женат/Не замужем", "Женат/Замужем", "Разведен(а)", "Вдовец/Вдова"],
        "US": ["Single", "Married", "Divorced", "Widowed"],
        "GB": ["Single", "Married", "Divorced", "Widowed"],
        "DE": ["Ledig", "Verheiratet", "Geschieden", "Verwitwet"],
        "FR": ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"]
    }

    _social_media = ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok"]

    # Расширенный список почтовых доменов
    _email_domains = {
        "RU": [
            "mail.ru", "yandex.ru", "rambler.ru", "gmail.com", "yahoo.com",
            "outlook.com", "hotmail.com", "list.ru", "bk.ru", "inbox.ru",
            "internet.ru", "yahoo.ru", "yandex.com", "mail.com"
        ],
        "US": [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "zoho.com", "mail.com", "live.com",
            "msn.com", "comcast.net", "verizon.net", "att.net"
        ],
        "GB": [
            "gmail.com", "yahoo.co.uk", "hotmail.co.uk", "outlook.com",
            "googlemail.com", "btinternet.com", "mail.com", "protonmail.com",
            "icloud.com", "live.co.uk", "sky.com", "aol.co.uk", "virgin.net"
        ],
        "DE": [
            "gmail.com", "yahoo.de", "hotmail.de", "outlook.de", "web.de",
            "gmx.de", "t-online.de", "mail.de", "protonmail.com", "freenet.de"
        ],
        "FR": [
            "gmail.com", "yahoo.fr", "hotmail.fr", "outlook.fr", "orange.fr",
            "laposte.net", "free.fr", "sfr.fr", "protonmail.com", "wanadoo.fr"
        ]
    }

    # Расширенный список стран и городов
    _countries = {
        "RU": {
            "name": "Россия",
            "phone_prefix": "+7",
            "postal_code_format": "######",
            "address_format": "г. {city}, ул. {street}, д. {house}, кв. {apartment}",
            "cities": [
                "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
                "Казань", "Нижний Новгород", "Челябинск", "Самара", "Омск",
                "Ростов-на-Дону", "Уфа", "Красноярск", "Воронеж", "Пермь",
                "Волгоград", "Краснодар", "Саратов", "Тюмень", "Тольятти",
                "Ижевск", "Барнаул", "Иркутск", "Ульяновск", "Хабаровск",
                "Ярославль", "Владивосток", "Махачкала", "Томск", "Оренбург"
            ],
            "streets": [
                "Ленина", "Пушкина", "Гагарина", "Мира", "Советская",
                "Центральная", "Молодежная", "Школьная", "Лесная", "Садовая",
                "Парковая", "Зеленая", "Комсомольская", "Первомайская",
                "Набережная", "Московская", "Октябрьская", "Северная",
                "Южная", "Восточная", "Западная", "Солнечная", "Цветочная",
                "Заводская", "Новая", "Полевая", "Луговая", "Речная"
            ],
            "first_names_male": [
                "Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей", "Артём",
                "Илья", "Кирилл", "Михаил", "Никита", "Матвей", "Роман", "Егор", "Арсений",
                "Иван", "Денис", "Евгений", "Даниил", "Тимофей"
            ],
            "first_names_female": [
                "Анна", "Мария", "Елена", "Дарья", "София", "Алиса", "Виктория",
                "Полина", "Екатерина", "Ксения", "Александра", "Варвара", "Анастасия",
                "Вероника", "Алина", "Ирина", "Марина", "Светлана", "Юлия", "Татьяна"
            ],
            "last_names_male": [
                "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров",
                "Соколов", "Михайлов", "Новиков", "Федоров", "Морозов", "Волков",
                "Алексеев", "Лебедев", "Семенов", "Егоров", "Павлов", "Козлов"
            ],
            "last_names_female": [
                "Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева", "Петрова",
                "Соколова", "Михайлова", "Новикова", "Федорова", "Морозова", "Волкова",
                "Алексеева", "Лебедева", "Семенова", "Егорова", "Павлова", "Козлова"
            ]
        },
        "US": {
            "name": "United States",
            "phone_prefix": "+1",
            "postal_code_format": "#####",
            "address_format": "{house} {street} {street_suffix}, {city}, {state} {postal_code}",
            "cities": [
                "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
                "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco",
                "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington",
                "Boston", "El Paso", "Detroit", "Nashville", "Portland",
                "Memphis", "Oklahoma City", "Las Vegas", "Louisville", "Baltimore"
            ],
            "streets": [
                "Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington",
                "Lake", "Hill", "Park", "River", "Valley", "Forest", "Garden",
                "Meadow", "Ridge", "Spring", "Highland", "Union", "Church",
                "Mill", "Sunset", "Railroad", "Market", "Water", "Bridge",
                "Pearl", "Central", "Grove", "Franklin"
            ],
            "street_suffixes": [
                "Street", "Avenue", "Road", "Drive", "Boulevard", "Lane",
                "Way", "Circle", "Court", "Place", "Trail", "Parkway",
                "Plaza", "Square", "Terrace", "Path", "Highway", "Run",
                "Loop", "Alley"
            ],
            "states": [
                "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
            ],
            "first_names_male": [
                "James", "John", "Robert", "Michael", "William", "David", "Richard",
                "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
                "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth"
            ],
            "first_names_female": [
                "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
                "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret",
                "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"
            ],
            "last_names_male": [
                "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
            ],
            "last_names_female": [
                "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
            ]
        },
        "GB": {
            "name": "United Kingdom",
            "phone_prefix": "+44",
            "postal_code_format": "AA# #AA",
            "address_format": "{house} {street}, {city}, {postal_code}",
            "cities": [
                "London", "Birmingham", "Leeds", "Glasgow", "Sheffield",
                "Manchester", "Edinburgh", "Liverpool", "Bristol", "Cardiff",
                "Belfast", "Newcastle", "Nottingham", "Southampton", "Portsmouth",
                "Aberdeen", "Brighton", "Cambridge", "Oxford", "York",
                "Leicester", "Coventry", "Hull", "Bradford", "Stoke-on-Trent",
                "Plymouth", "Derby", "Swansea", "Sunderland", "Reading"
            ],
            "streets": [
                "High", "Station", "Main", "Church", "Park", "Victoria",
                "Green", "Manor", "Kings", "Queens", "Albert", "London",
                "York", "George", "Market", "North", "South", "East",
                "West", "Bridge", "Castle", "Mill", "Grove", "New",
                "Old", "School", "Richmond", "Windsor", "Bath", "Oxford"
            ],
            "first_names_male": [
                "Oliver", "Jack", "Harry", "George", "Noah", "Charlie", "Jacob",
                "Oscar", "Muhammad", "William", "Leo", "Henry", "Thomas", "Ethan",
                "Alexander", "Daniel", "Arthur", "James", "Frederick", "Edward"
            ],
            "first_names_female": [
                "Olivia", "Emma", "Ava", "Isabella", "Sophia", "Charlotte", "Mia",
                "Amelia", "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth",
                "Sofia", "Ella", "Madison", "Scarlett", "Victoria", "Grace", "Chloe"
            ],
            "last_names_male": [
                "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans",
                "Wilson", "Thomas", "Johnson", "Roberts", "Walker", "Wright", "Robinson",
                "Thompson", "White", "Hughes", "Edwards", "Green", "Hall"
            ],
            "last_names_female": [
                "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans",
                "Wilson", "Thomas", "Johnson", "Roberts", "Walker", "Wright", "Robinson",
                "Thompson", "White", "Hughes", "Edwards", "Green", "Hall"
            ]
        },
        "DE": {
            "name": "Deutschland",
            "phone_prefix": "+49",
            "postal_code_format": "#####",
            "address_format": "{street} {house}, {postal_code} {city}",
            "cities": [
                "Berlin", "Hamburg", "München", "Köln", "Frankfurt",
                "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen",
                "Bremen", "Dresden", "Hannover", "Nürnberg", "Duisburg",
                "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster",
                "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden", "Gelsenkirchen",
                "Mönchengladbach", "Braunschweig", "Kiel", "Aachen", "Magdeburg"
            ],
            "streets": [
                "Hauptstraße", "Schulstraße", "Bahnhofstraße", "Gartenstraße",
                "Kirchstraße", "Bergstraße", "Waldstraße", "Ringstraße",
                "Parkstraße", "Lindenstraße", "Friedhofstraße", "Marktstraße",
                "Rosenstraße", "Mühlenweg", "Schillerstraße", "Goethestraße",
                "Mozartstraße", "Beethovenstraße", "Bismarckstraße", "Uhlandstraße"
            ],
            "first_names_male": [
                "Alexander", "Maximilian", "Paul", "Leon", "Luis", "Luca", "Felix",
                "Jonas", "David", "Elias", "Julian", "Finn", "Noah", "Benjamin",
                "Niklas", "Daniel", "Simon", "Jakob", "Lucas", "Rafael"
            ],
            "first_names_female": [
                "Emma", "Mia", "Hannah", "Sofia", "Anna", "Lea", "Emilia", "Marie",
                "Lena", "Leonie", "Julia", "Laura", "Sarah", "Lisa", "Lara",
                "Victoria", "Elena", "Amelie", "Clara", "Sophie"
            ],
            "last_names_male": [
                "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
                "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter",
                "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann"
            ],
            "last_names_female": [
                "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
                "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter",
                "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann"
            ]
        },
        "FR": {
            "name": "France",
            "phone_prefix": "+33",
            "postal_code_format": "#####",
            "address_format": "{house} {street}, {postal_code} {city}",
            "cities": [
                "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
                "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
                "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon",
                "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne",
                "Le Mans", "Aix-en-Provence", "Brest", "Tours", "Amiens",
                "Limoges", "Clermont-Ferrand", "Besançon", "Metz", "Caen"
            ],
            "streets": [
                "Rue de la République", "Rue de Paris", "Rue de l'Église",
                "Avenue des Champs-Élysées", "Boulevard Saint-Michel",
                "Rue Victor Hugo", "Avenue Jean Jaurès", "Rue Pasteur",
                "Boulevard de la Liberté", "Rue du Commerce", "Place de la Mairie",
                "Rue des Écoles", "Avenue de la Gare", "Rue de la Paix",
                "Boulevard Gambetta", "Rue Émile Zola", "Avenue Foch",
                "Rue Saint-Jacques", "Place de la République", "Rue Nationale"
            ],
            "first_names_male": [
                "Gabriel", "Louis", "Raphaël", "Jules", "Adam", "Lucas", "Léo",
                "Hugo", "Arthur", "Nathan", "Thomas", "Paul", "Alexandre", "Antoine",
                "Maxime", "Baptiste", "Nicolas", "Mohamed", "Théo", "Ethan"
            ],
            "first_names_female": [
                "Emma", "Louise", "Jade", "Alice", "Chloé", "Lina", "Léa", "Rose",
                "Anna", "Mila", "Julia", "Marie", "Inès", "Zoé", "Sarah",
                "Camille", "Sofia", "Charlotte", "Manon", "Juliette"
            ],
            "last_names_male": [
                "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
                "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
                "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier"
            ],
            "last_names_female": [
                "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
                "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
                "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier"
            ]
        }
    }

    # Словарь для транслитерации
    _translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    @classmethod
    def _transliterate(cls, text: str) -> str:
        """Преобразует кириллицу в латиницу."""
        result = ""
        for char in text:
            result += cls._translit_dict.get(char, char)
        return result

    @classmethod
    def generate_user(cls, country_code: str = "RU", gender: Optional[str] = None, password_settings: Optional[str] = None) -> Dict[str, Union[str, int, List[str]]]:
        """Генерирует случайного пользователя."""
        try:
            # Проверяем и нормализуем входные данные
            country_code = country_code.upper()
            if country_code not in cls._countries:
                country_code = "RU"
            
            # Определяем пол, если не указан
            if gender not in ["male", "female"]:
                gender = random.choice(["male", "female"])
            
            # Получаем данные страны
            country_data = cls._countries[country_code]
            
            # Генерируем основные данные
            first_name = random.choice(
                country_data["first_names_male" if gender == "male" else "first_names_female"]
            )
            last_name = random.choice(
                country_data["last_names_male" if gender == "male" else "last_names_female"]
            )
            
            # Генерируем email с транслитерацией
            email = cls._generate_email(first_name, last_name, country_code)
            
            # Генерируем социальные сети
            social_media = {}
            for platform in random.sample(cls._social_media, random.randint(2, 4)):
                username = cls._generate_social_media_username(first_name, last_name)
                social_media[platform] = username

            # Генерируем данные для входа
            login_username = cls._generate_social_media_username(first_name, last_name)
            password = generate_password(password_settings)

            # Остальные данные генерируются как обычно
            address = cls._generate_address(country_code)
            phone = cls._generate_phone(country_code)
            birth_date = cls._generate_birth_date()
            age = datetime.now().year - birth_date.year
            
            physical = {
                "height": random.randint(150, 200),
                "weight": random.randint(45, 120),
                "blood_type": random.choice(cls._blood_types)
            }
            
            education = {
                "level": random.choice(cls._education_levels[country_code]),
                "university": random.choice(cls._universities[country_code]),
                "graduation_year": datetime.now().year - random.randint(0, 40)
            }
            
            occupation = random.choice(cls._occupations[country_code])
            languages = random.sample(cls._languages[country_code], random.randint(1, 3))
            hobbies = random.sample(cls._hobbies[country_code], random.randint(2, 4))
            marital_status = random.choice(cls._marital_status[country_code])
            
            # Формируем результат
            return {
                "gender": gender,
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "email": email,
                "phone": phone,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "age": age,
                "physical": physical,
                "education": education,
                "occupation": occupation,
                "languages": languages,
                "hobbies": hobbies,
                "marital_status": marital_status,
                "social_media": social_media,
                "login": {
                    "username": login_username,
                    "password": password
                },
                "country": country_data["name"]
            }
        except Exception as e:
            logger.error(f"Error in generate_user: {str(e)}")
            raise

    @classmethod
    def generate_users(cls, count: int, country_code: str = "RU", gender: Optional[str] = None) -> List[Dict[str, Union[str, int, List[str]]]]:
        """Генерирует несколько случайных пользователей."""
        return [cls.generate_user(country_code, gender) for _ in range(count)]

    @staticmethod
    def _generate_id() -> int:
        """Генерирует случайный ID."""
        return random.randint(10000, 99999)

    @classmethod
    def _generate_birth_date(cls) -> datetime:
        """Генерирует случайную дату рождения с более реалистичным распределением."""
        today = datetime.now()
        # Расширяем диапазон возрастов (от 18 до 90 лет)
        start_date = today - timedelta(days=365 * 90)
        end_date = today - timedelta(days=365 * 18)
        
        # Используем нормальное распределение для более реалистичного возраста
        mean_age = 35
        std_dev = 15
        age = int(random.gauss(mean_age, std_dev))
        
        # Ограничиваем возраст в пределах 18-90 лет
        age = max(18, min(90, age))
        
        birth_date = today - timedelta(days=365 * age)
        
        # Добавляем случайное количество дней в пределах года
        birth_date += timedelta(days=random.randint(0, 365))
        
        return birth_date

    @classmethod
    def _generate_email(cls, first_name: str, last_name: str, country_code: str) -> str:
        """Генерирует email адрес."""
        # Транслитерация имени и фамилии
        first_name = cls._transliterate(first_name.lower())
        last_name = cls._transliterate(last_name.lower())
        
        # Удаляем все символы, кроме букв и цифр
        first_name = ''.join(c for c in first_name if c.isalnum())
        last_name = ''.join(c for c in last_name if c.isalnum())
        
        # Генерируем варианты username
        username_variants = [
            f"{first_name}{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name[0]}{last_name}",
            f"{first_name}{last_name[:3]}",
            f"{first_name[:3]}{last_name[:3]}"
        ]
        username = random.choice(username_variants)
        
        # Добавляем случайные цифры, если нужно
        if random.random() < 0.7:  # 70% шанс добавления цифр
            username += str(random.randint(1, 9999))
        
        domain = random.choice(cls._email_domains[country_code])
        return f"{username}@{domain}"

    @classmethod
    def _generate_address(cls, country_code: str) -> str:
        """Генерирует адрес."""
        country_data = cls._countries[country_code]
        city = random.choice(country_data["cities"])
        street = random.choice(country_data["streets"])
        house = str(random.randint(1, 150))
        apartment = str(random.randint(1, 100))
        
        if country_code == "RU":
            return f"г. {city}, ул. {street}, д. {house}, кв. {apartment}"
        elif country_code == "US":
            street_suffix = random.choice(country_data["street_suffixes"])
            state = random.choice(country_data["states"])
            postal_code = f"{random.randint(10000, 99999)}"
            return f"{house} {street} {street_suffix}, {city}, {state} {postal_code}"
        else:
            return f"{house} {street} St., {city}"

    @staticmethod
    def _generate_uk_postal_code() -> str:
        """Генерирует почтовый индекс в формате UK."""
        area = random.choice(["SW", "SE", "NW", "NE", "W", "E", "N", "S"])
        district = random.randint(1, 99)
        sector = random.randint(1, 9)
        unit = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}"
        return f"{area}{district} {sector}{unit}"

    @classmethod
    def _generate_phone(cls, country_code: str) -> str:
        """Генерирует номер телефона с учетом реальных форматов."""
        country_data = cls._countries[country_code]
        prefix = country_data["phone_prefix"]
        
        if country_code == "RU":
            operators = ["900", "901", "902", "903", "904", "905", "906", "908", "909",
                       "910", "911", "912", "913", "914", "915", "916", "917", "918",
                       "919", "920", "921", "922", "923", "924", "925", "926", "927",
                       "928", "929", "930", "931", "932", "933", "934", "935", "936",
                       "937", "938", "939", "950", "951", "952", "953", "954", "955",
                       "956", "957", "958", "959", "960", "961", "962", "963", "964",
                       "965", "966", "967", "968", "969", "980", "981", "982", "983",
                       "984", "985", "986", "987", "988", "989", "999"]
            return f"{prefix} {random.choice(operators)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
        elif country_code == "US":
            area_codes = ["201", "202", "203", "205", "206", "207", "208", "209", "210",
                         "212", "213", "214", "215", "216", "217", "218", "219", "220",
                         "223", "224", "225", "227", "228", "229", "231", "234", "239",
                         "240", "248", "251", "252", "253", "254", "256", "260", "262",
                         "267", "269", "270", "272", "276", "281", "283", "301", "302",
                         "303", "304", "305", "307", "308", "309", "310", "312", "313",
                         "314", "315", "316", "317", "318", "319", "320", "321", "323",
                         "325", "327", "330", "331", "334", "336", "337", "339", "346",
                         "347", "351", "352", "360", "361", "364", "380", "385", "386",
                         "401", "402", "404", "405", "406", "407", "408", "409", "410",
                         "412", "413", "414", "415", "417", "419", "423", "424", "425",
                         "430", "432", "434", "435", "440", "442", "443", "447", "458",
                         "463", "469", "470", "475", "478", "479", "480", "484", "501",
                         "502", "503", "504", "505", "507", "508", "509", "510", "512",
                         "513", "515", "516", "517", "518", "520", "530", "531", "534",
                         "539", "540", "541", "551", "559", "561", "562", "563", "564",
                         "567", "570", "571", "573", "574", "575", "580", "585", "586",
                         "601", "602", "603", "605", "606", "607", "608", "609", "610",
                         "612", "614", "615", "616", "617", "618", "619", "620", "623",
                         "626", "628", "629", "630", "631", "636", "641", "646", "650",
                         "651", "657", "660", "661", "662", "667", "669", "678", "681",
                         "682", "701", "702", "703", "704", "706", "707", "708", "712",
                         "713", "714", "715", "716", "717", "718", "719", "720", "724",
                         "725", "727", "730", "731", "732", "734", "737", "740", "743",
                         "747", "754", "757", "760", "762", "763", "765", "769", "770",
                         "772", "773", "774", "775", "779", "781", "785", "786", "801",
                         "802", "803", "804", "805", "806", "808", "810", "812", "813",
                         "814", "815", "816", "817", "818", "828", "830", "831", "832",
                         "843", "845", "847", "848", "850", "854", "856", "857", "858",
                         "859", "860", "862", "863", "864", "865", "870", "872", "878",
                         "901", "903", "904", "906", "907", "908", "909", "910", "912",
                         "913", "914", "915", "916", "917", "918", "919", "920", "925",
                         "928", "929", "930", "931", "934", "936", "937", "938", "940",
                         "941", "947", "949", "951", "952", "954", "956", "959", "970",
                         "971", "972", "973", "975", "978", "979", "980", "984", "985",
                         "989"]
            return f"{prefix} ({random.choice(area_codes)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        else:
            return f"{prefix} {random.randint(100000000, 999999999)}"

    @classmethod
    def get_available_countries(cls) -> List[str]:
        """Возвращает список доступных стран."""
        return list(cls._countries.keys())

    @classmethod
    def _generate_social_media_username(cls, first_name: str, last_name: str) -> str:
        """Генерирует username для социальных сетей."""
        # Транслитерация и подготовка имени и фамилии
        first_name = cls._transliterate(first_name.lower())
        last_name = cls._transliterate(last_name.lower())
        
        # Удаляем все символы, кроме букв и цифр
        first_name = ''.join(c for c in first_name if c.isalnum())
        last_name = ''.join(c for c in last_name if c.isalnum())
        
        # Генерируем варианты username
        username_variants = [
            f"{first_name}{last_name}",
            f"{first_name}_{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name[0]}{last_name}",
            f"the_{first_name}",
            f"real_{first_name}",
            f"{first_name}{random.randint(1, 999)}"
        ]
        
        username = random.choice(username_variants)
        
        # Добавляем случайные цифры или символы
        if random.random() < 0.5:  # 50% шанс добавления
            if random.random() < 0.7:  # 70% шанс цифр, 30% шанс символов
                username += str(random.randint(1, 9999))
            else:
                username += random.choice(["_official", "_real", "_original", "_me"])
        
        return username 

    def format_user_data(self, user_data: Dict[str, Union[str, int, List[str]]]) -> Dict[str, Union[str, int, List[str]]]:
        """Форматирует данные пользователя в нужный формат."""
        # Форматируем данные в нужный формат
        formatted_data = {
            "results": [{
                "name": {
                    "first": user_data.get("first_name", ""),
                    "last": user_data.get("last_name", "")
                },
                "gender": user_data.get("gender", ""),
                "location": {
                    "street": {
                        "name": user_data.get("address", "").split(",")[0] if "," in user_data.get("address", "") else "",
                        "number": ""
                    },
                    "city": user_data.get("address", "").split(",")[1].strip() if "," in user_data.get("address", "") else "",
                    "country": user_data.get("country", "")
                },
                "email": user_data.get("email", ""),
                "login": {
                    "username": user_data.get("email", "").split("@")[0] if "@" in user_data.get("email", "") else "",
                    "password": user_data.get("password", "")
                },
                "phone": user_data.get("phone", ""),
                "cell": user_data.get("phone", ""),
                "dob": {
                    "date": user_data.get("birth_date", ""),
                    "age": user_data.get("age", 0)
                },
                "physical": user_data.get("physical", {}),
                "education": user_data.get("education", {}),
                "occupation": user_data.get("occupation", ""),
                "languages": user_data.get("languages", []),
                "hobbies": user_data.get("hobbies", []),
                "marital_status": user_data.get("marital_status", ""),
                "social_media": user_data.get("social_media", {})
            }]
        }
        return formatted_data 