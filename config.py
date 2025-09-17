# Configuration for AfD Twitter Bot
# This file contains the accounts to monitor and keywords to search for

# Official AfD Twitter accounts (federal and state level)
AFD_ACCOUNTS = [
    # Federal level
    "AfD",
    "Alice_Weidel", 
    "Tino_Chrupalla",
    "AfDimBundestag",
    
    # State level accounts (major states)
    "AfD_Bayern",
    "AfD_BW",
    "AfDimLandtagNRW",
    "AfD_LSA",
    "AfD_Thueringen",
    "AfD_Brandenburg",
    "AfD_Sachsen",
    "AfDFraktionSH",
    "AfD_Berlin",
    "AfDBremen",
    "AfD_Hamburg",
    "AfD_Hessen",
    "AfD_MV",
    "AfD_Niedersachsen",
    "AfD_RLP",
    "AfD_Saarland"
]

# Keywords related to constitutional concerns
# Based on Article 21(2) of the German Basic Law
CONSTITUTIONAL_KEYWORDS = [
    # Against democratic basic order
    "demokratie abschaffen",
    "system stürzen", 
    "verfassung aufheben",
    "grundgesetz abschaffen",
    "republik beenden",
    "umsturz",
    "revolution",
    "widerstand leisten",
    
    # Against human dignity
    "menschenwürde",
    "untermenschen",
    "lebensunwert",
    "ausmerzen",
    "vernichten",
    
    # Against rule of law
    "rechtsstaat abschaffen",
    "gesetze ignorieren",
    "selbstjustiz",
    "lynchjustiz",
    
    # Against separation of powers
    "gewaltenteilung aufheben",
    "richter absetzen",
    "parlament auflösen",
    
    # Against multiparty system
    "einparteienherrschaft",
    "opposition verbieten",
    "parteien abschaffen",
    
    # Extremist references
    "drittes reich",
    "nationalsozialismus",
    "hitler",
    "ns-zeit",
    "völkermord",
    "holocaust leugnung",
    "rassenhygiene",
    "endlösung",
    
    # Violence promotion
    "gewalt anwenden",
    "kampf gegen",
    "vernichtung",
    "ausrottung",
    "säuberung",
    "pogrom",
    
    # Anti-constitutional language
    "verfassungsfeindlich",
    "staatsfeind",
    "reichsbürger",
    "souverän",
    "besatzung",
    "befreiung deutschlands"
]

# Content categories for classification
CONTENT_CATEGORIES = {
    "anti_democratic": [
        "demokratie abschaffen", "system stürzen", "verfassung aufheben",
        "grundgesetz abschaffen", "umsturz", "revolution"
    ],
    "hate_speech": [
        "untermenschen", "lebensunwert", "ausmerzen", "vernichten",
        "rassenhygiene", "säuberung", "pogrom"
    ],
    "historical_revisionism": [
        "drittes reich", "hitler", "holocaust leugnung", "ns-zeit",
        "endlösung", "völkermord"
    ],
    "violence_promotion": [
        "gewalt anwenden", "kampf gegen", "vernichtung", "ausrottung",
        "selbstjustiz", "lynchjustiz"
    ],
    "anti_constitutional": [
        "verfassungsfeindlich", "staatsfeind", "reichsbürger",
        "rechtsstaat abschaffen", "gewaltenteilung aufheben"
    ]
}

# Search settings
SEARCH_SETTINGS = {
    "max_tweets_per_account": 100,
    "days_back": 30,
    "language": "de",
    "result_type": "recent",
    # Interval for watch mode (seconds). 30 is possible, but default longer to save credits
    "poll_interval_seconds": 600
}
