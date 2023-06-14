import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from dashboard.models import Course

class HybridRecommender:
    
    def __init__(self) -> None:
        # self.df = pd.DataFrame(list(Course().get_all()))
        pass
        
    # Function that computes the weighted rating of each course
    def weighted_rating(self, x, m, C):
        v = x['review_count']
        R = x['rating']
        # Calculation based on the IMDB formula
        return (v/(v+m) * R) + (m/(m+v) * C)
    
    def filter_courses_by_topic(self, topic):
        self.df = pd.DataFrame(list(Course().get_by_topic(topic)))
        return self.df[self.df['topics'].str.contains(topic, na=False)]
    
    def get_base_recommendations(self, interest):
        topic_of_interest = interest.lower()
        self.df = self.filter_courses_by_topic(topic_of_interest)
        self.df['topics'] = self.df['topics'].fillna('')

        # Calculate mean rating across all courses
        C = self.df['rating'].mean()

        # Calculate the minimum number of reviews required to be in the chart. Let's take 90th percentile as our cutoff. 
        m = self.df['review_count'].quantile(0.9)
        
        # Define a new feature 'score' and calculate its value with `weighted_rating()`
        self.df['score'] = self.df.apply(lambda x: self.weighted_rating(x, m, C), axis=1)

        # Return the top 10 most popular courses, grouped by website and sorted by the score
        return self.df.groupby('website').apply(lambda x: x.nlargest(10, 'score')).reset_index(drop=True)
    
    def get_recommendations(self, interest, course_name):
        topic_of_interest = interest.lower()
        self.df = self.filter_courses_by_topic(topic_of_interest)
        self.df['topics'] = self.df['topics'].fillna('')

        # Initialize the TfidfVectorizer 
        tfidf = TfidfVectorizer(stop_words='english')

        # Construct the TF-IDF matrix
        tfidf_matrix = tfidf.fit_transform(self.df['topics'])

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        # Create a reverse map of indices and course titles
        indices = pd.Series(self.df.index, index=self.df['course_name']).drop_duplicates()

        # Calculate mean rating across all courses
        C = self.df['rating'].mean()

        # Calculate the minimum number of reviews required to be in the chart. Let's take 90th percentile as our cutoff. 
        m = self.df['review_count'].quantile(0.9)
        
        # Define a new feature 'score' and calculate its value with `weighted_rating()`
        self.df['score'] = self.df.apply(lambda x: self.weighted_rating(x, m, C), axis=1)

        # Get the index of the course that matches the title
        idx = indices[course_name]

        # Get the pairwise similarity scores of all courses with that course
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the courses based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar courses
        sim_scores = sim_scores[1:11]

        # Get the course indices
        course_indices = [i[0] for i in sim_scores]
        
        # Get the top 10 similar courses
        top_courses = self.df.iloc[course_indices].copy()

        # Compute a new score that takes into account both similarity and popularity
        # Let's give 50% importance to the similarity score and 50% to the popularity score
        top_courses['hybrid_score'] = top_courses['score'] * 0.5 + sim_scores[1][1] * 0.5

        # Return the top 10 most similar courses, grouped by website and sorted by the new hybrid score
        return top_courses.groupby('website').apply(lambda x: x.sort_values('hybrid_score', ascending=False)).reset_index(drop=True)
        