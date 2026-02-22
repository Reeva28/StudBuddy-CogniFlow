"""
Text summarization and question generation service
"""
import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import traceback

# Download NLTK data (uncomment for first run)
# nltk.download('punkt')
# nltk.download('stopwords')

# Check if sentence-transformers is available, otherwise use TF-IDF
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    USE_SEMANTIC = True
    model = SentenceTransformer('all-MiniLM-L6-v2')
except (ImportError, OSError, RuntimeError) as e:
    print(f"sentence-transformers not available ({type(e).__name__}), falling back to TF-IDF")
    USE_SEMANTIC = False

def preprocess_text(text: str) -> str:
    """
    Clean and preprocess text
    """
    # Remove multiple line breaks and whitespace
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = re.sub(r'[^\w\s.,?!]', '', text)
    
    return text.strip()

def get_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    """
    # Add a space after period if not present to help sentence tokenization
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Split into sentences
    sentences = sent_tokenize(text)
    
    # Clean sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    return sentences

def generate_summary(text: str, max_sentences: int = 10) -> str:
    """
    Generate a summary of the text using extractive summarization
    """
    try:
        # Preprocess text
        clean_text = preprocess_text(text)
        
        # Check if text is too short to summarize
        if len(clean_text) < 200:
            return clean_text
        
        # Get sentences
        sentences = get_sentences(clean_text)
        
        if len(sentences) <= max_sentences:
            return " ".join(sentences)
        
        # Use semantic similarity if available, otherwise use TF-IDF
        if USE_SEMANTIC:
            # Encode sentences
            sentence_embeddings = model.encode(sentences)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(sentence_embeddings)
            
            # Calculate sentence scores
            scores = np.sum(similarity_matrix, axis=1)
            
            # Get top sentences
            top_indices = scores.argsort()[-max_sentences:]
            top_indices = sorted(top_indices)
            
            # Extract top sentences
            summary_sentences = [sentences[i] for i in top_indices]
            
            return " ".join(summary_sentences)
        else:
            # Use TF-IDF for summarization
            vectorizer = TfidfVectorizer(stop_words='english')
            sentence_vectors = vectorizer.fit_transform(sentences)
            
            # Get sentence scores
            scores = sentence_vectors.sum(axis=1).A1
            
            # Get top sentences
            top_indices = scores.argsort()[-max_sentences:]
            top_indices = sorted(top_indices)
            
            # Extract top sentences
            summary_sentences = [sentences[i] for i in top_indices]
            
            return " ".join(summary_sentences)
    
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        traceback.print_exc()
        return text[:1000] + "..." if len(text) > 1000 else text

def generate_key_points(text: str, max_points: int = 5) -> List[str]:
    """
    Extract key points from the text
    """
    try:
        # Preprocess text
        clean_text = preprocess_text(text)
        
        # Get sentences
        sentences = get_sentences(clean_text)
        
        if len(sentences) <= max_points:
            return sentences
        
        # Use semantic similarity if available, otherwise use TF-IDF
        if USE_SEMANTIC:
            # Encode sentences
            sentence_embeddings = model.encode(sentences)
            
            # Calculate sentence importance
            # For key points, we want diverse and important sentences
            similarity_matrix = cosine_similarity(sentence_embeddings)
            
            # Initialize selection
            selected = []
            remaining = list(range(len(sentences)))
            
            # First, select the most central sentence
            avg_sim = np.mean(similarity_matrix, axis=1)
            first_idx = np.argmax(avg_sim)
            selected.append(first_idx)
            remaining.remove(first_idx)
            
            # Then select sentences that are important but different from already selected ones
            for _ in range(min(max_points - 1, len(remaining))):
                best_idx = -1
                best_score = -float('inf')
                
                for idx in remaining:
                    # Calculate relevance (importance)
                    relevance = np.mean(similarity_matrix[idx])
                    
                    # Calculate diversity (difference from already selected sentences)
                    diversity = -np.mean([similarity_matrix[idx, sel_idx] for sel_idx in selected])
                    
                    # Combined score: balance relevance and diversity
                    score = relevance + 0.7 * diversity
                    
                    if score > best_score:
                        best_score = score
                        best_idx = idx
                
                if best_idx >= 0:
                    selected.append(best_idx)
                    remaining.remove(best_idx)
            
            # Sort selected indices
            selected.sort()
            
            # Format as key points
            key_points = [f"{sentences[i]}" for i in selected]
            
            return key_points
        else:
            # Use TF-IDF for key points
            vectorizer = TfidfVectorizer(stop_words='english')
            sentence_vectors = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Score sentences based on TF-IDF
            scores = {}
            for i, sentence in enumerate(sentences):
                for j, word in enumerate(vectorizer.get_feature_names_out()):
                    if sentence_vectors[i, j] > 0:
                        if i not in scores:
                            scores[i] = 0
                        scores[i] += sentence_vectors[i, j]
            
            # Get top sentences
            top_indices = sorted(scores, key=scores.get, reverse=True)[:max_points]
            top_indices.sort()
            
            # Format as key points
            key_points = [f"{sentences[i]}" for i in top_indices]
            
            return key_points
    
    except Exception as e:
        print(f"Error generating key points: {str(e)}")
        traceback.print_exc()
        return ["Unable to generate key points due to an error."]

def generate_flashcards(text: str, count: int = 10) -> List[Dict[str, str]]:
    """
    Generate flashcards (question-answer pairs) from text
    """
    try:
        # Preprocess text
        clean_text = preprocess_text(text)
        
        # Get sentences
        sentences = get_sentences(clean_text)
        
        # Select sentences for flashcards
        if len(sentences) <= count:
            selected_sentences = sentences
        else:
            # Use TF-IDF to select informative sentences
            vectorizer = TfidfVectorizer(stop_words='english')
            sentence_vectors = vectorizer.fit_transform(sentences)
            
            # Score sentences
            scores = sentence_vectors.sum(axis=1).A1
            
            # Get top sentences
            top_indices = scores.argsort()[-count:]
            selected_sentences = [sentences[i] for i in top_indices]
        
        flashcards = []
        
        for sentence in selected_sentences:
            # For simple flashcards, convert statements to questions
            words = word_tokenize(sentence)
            
            # Skip very short sentences
            if len(words) < 5:
                continue
                
            # Simple approach: look for key information to hide
            key_terms = []
            for word in words:
                if len(word) > 4 and word.lower() not in stopwords.words('english'):
                    key_terms.append(word)
            
            if key_terms:
                # Select a random key term to hide
                import random
                term = random.choice(key_terms)
                
                # Create question by replacing the term with a blank
                question = sentence.replace(term, "________")
                
                flashcards.append({
                    "question": question,
                    "answer": term
                })
        
        return flashcards
    
    except Exception as e:
        print(f"Error generating flashcards: {str(e)}")
        traceback.print_exc()
        return [{"question": "What is the main topic of this text?", "answer": "Review the text to answer this question."}]

def generate_quiz(text: str, question_count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate multiple-choice questions from text
    """
    try:
        # Preprocess text
        clean_text = preprocess_text(text)
        
        # Get sentences
        sentences = get_sentences(clean_text)
        
        # For a simple implementation, create cloze questions
        questions = []
        
        # Use TF-IDF to find important sentences
        vectorizer = TfidfVectorizer(stop_words='english')
        sentence_vectors = vectorizer.fit_transform(sentences)
        
        # Score sentences
        scores = sentence_vectors.sum(axis=1).A1
        
        # Get top sentences for questions
        top_indices = scores.argsort()[-question_count*2:]  # Get more sentences than needed in case some don't make good questions
        selected_sentences = [sentences[i] for i in top_indices]
        
        # Get important terms from the text
        important_terms = []
        feature_names = vectorizer.get_feature_names_out()
        for i, sentence in enumerate(sentences):
            for j, word in enumerate(feature_names):
                if sentence_vectors[i, j] > 0.1:  # Only consider terms with high TF-IDF score
                    important_terms.append(word)
        
        # Remove duplicates and limit
        important_terms = list(set(important_terms))[:30]
        
        question_count = min(question_count, len(selected_sentences))
        
        for i in range(question_count):
            sentence = selected_sentences[i]
            words = word_tokenize(sentence)
            
            # Find important words
            candidates = []
            for word in words:
                if (len(word) > 4 and word.lower() not in stopwords.words('english') 
                    and word.isalpha() and word.lower() in important_terms):
                    candidates.append(word)
            
            if not candidates:
                continue
                
            # Select a random candidate
            import random
            answer = random.choice(candidates)
            
            # Create question by replacing the answer with a blank
            question_text = sentence.replace(answer, "________")
            
            # Create distractors (wrong answers)
            # Use other important terms as distractors
            distractors = []
            for term in important_terms:
                if term != answer.lower() and term not in distractors:
                    distractors.append(term.capitalize() if answer[0].isupper() else term)
                    if len(distractors) == 3:
                        break
            
            # If not enough distractors, add some common words
            common_words = ["Factor", "Process", "Element", "Function", "System", "Concept"]
            while len(distractors) < 3:
                word = random.choice(common_words)
                if word not in distractors:
                    distractors.append(word)
            
            # Create the question
            question = {
                "question": question_text,
                "options": [answer] + distractors,
                "answer": answer
            }
            
            # Shuffle options
            random.shuffle(question["options"])
            
            questions.append(question)
        
        return questions
    
    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        traceback.print_exc()
        return [{"question": "What is the main topic of this text?", 
                "options": ["Answer A", "Answer B", "Answer C", "Answer D"], 
                "answer": "Answer A"}]