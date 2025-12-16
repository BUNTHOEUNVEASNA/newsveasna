import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from .models import Category

# Pre-load required NLTK resources (run nltk.download('punkt') and nltk.download('stopwords') once)
try:
    STOP_WORDS = set(stopwords.words('english'))
except LookupError:
    # Handle the case where the user hasn't downloaded resources yet
    print("NLTK resources not found. Please run 'import nltk; nltk.download(\"punkt\"); nltk.download(\"stopwords\")'")
    STOP_WORDS = set()
    

# Simple mapping of keywords to Category names (must match names in Category model)
# In a real app, this mapping could be stored in a database config table.
KEYWORD_MAP = {
    'tech': ['ai', 'software', 'startup', 'server', 'gadget'],
    'finance': ['stock', 'market', 'economy', 'investment', 'qtrly'],
    'sports': ['game', 'football', 'basket', 'championship', 'league'],
}

def categorize(text: str) -> list[str]:
    """
    System Action (Categorization): Runs text analysis (NLP/keywords) to assign one or more Categories.
    
    Args:
        text: The extracted article content.
        
    Returns:
        A list of category names (strings) assigned to the article.
    """
    # System Action (Categorization): Takes extracted content.
    if not text:
        return ["General"]
    
    # Tokenization and cleaning
    words = word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    filtered_words = [w for w in words if w.isalnum() and w not in STOP_WORDS]
    
    assigned_categories = set()
    
    # Simple keyword match for categorization
    for category_name, keywords in KEYWORD_MAP.items():
        if any(keyword in filtered_words for keyword in keywords):
            assigned_categories.add(category_name)
            
    if not assigned_categories:
        assigned_categories.add("General")
        
    return list(assigned_categories)