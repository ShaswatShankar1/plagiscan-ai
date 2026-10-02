from core.database import SessionLocal
from services.vector_search import index_document

def seed():
    db = SessionLocal()
    try:
        print("Seeding testing corpus to pgvector database...")
        
        index_document(db, "Intro to ML", "Machine learning algorithms can identify patterns in large datasets. This is highly useful for predictive analytics.")
        index_document(db, "Wikipedia: AI", "Artificial intelligence is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans.")
        index_document(db, "Data Science Basics", "A neural network is a network or circuit of biological neurons, or, in a modern sense, an artificial neural network.")
        index_document(db, "SEO Guide", "Search engine optimization represents the process of improving the quality and quantity of website traffic to a website or a web page from search engines.")
        
        print("Database seeding completed.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
