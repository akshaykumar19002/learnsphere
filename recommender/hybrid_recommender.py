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
    
    def get_base_recommendations(self, interest:str):
        topic_of_interest = interest.lower()
        self.df = self.filter_courses_by_topic(topic_of_interest)
        self.df['topics'] = self.df['topics'].fillna('')

        # Calculate mean rating across all courses
        C = self.df['rating'].mean()

        # Calculate the minimum number of reviews required to be in the chart. Let's take 90th percentile as our cutoff. 
        m = self.df['review_count'].quantile(0.9)
        
        # Define a new feature 'score' and calculate its value with `weighted_rating()`
        self.df['score'] = self.df.apply(lambda x: self.weighted_rating(x, m, C), axis=1)

        # Return the top 15 most popular courses, grouped by website and sorted by the score
        return self.df.groupby('website').apply(lambda x: x.nlargest(4, 'score')).reset_index(drop=True)
        # return self.df.nlargest(15, 'score').reset_index(drop=True)

    def get_base_recommendations_limited(self, limit:int=10):
        self.df['topics'] = self.df['topics'].fillna('')

        # Calculate mean rating across all courses
        C = self.df['rating'].mean()

        # Calculate the minimum number of reviews required to be in the chart. Let's take 90th percentile as our cutoff. 
        m = self.df['review_count'].quantile(0.9)
        
        # Define a new feature 'score' and calculate its value with `weighted_rating()`
        self.df['score'] = self.df.apply(lambda x: self.weighted_rating(x, m, C), axis=1)

        # Return the top 15 most popular courses, grouped by website and sorted by the score
        return self.df.groupby('website').apply(lambda x: x.nlargest(limit, 'score')).reset_index(drop=True)
    
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
        
        
    def get_list_of_topics(self, course_ids):
        courses =  list(Course().get_topic_by_ids(course_ids))
        topics = []
        for course in courses:
            course_topics = course['topics'].split()
            topics += course_topics
        return topics
    
    def filter_courses_by_topics(self, topics):
        self.df = pd.DataFrame(list(Course().get_by_topics(topics)))
        return self.df[self.df['topics'].str.contains('|'.join(topics), na=False)]
        
    def add_courses_to_df(self, course_ids):
        courses = list(Course().get_by_ids(course_ids))
        course_names = []
        for course in courses:
            if course['id'] not in self.df['id'].values:
                self.df = pd.concat([self.df, pd.DataFrame([course])], ignore_index=True)
                course_names.append(course['course_name'])
        return course_names
        
    def get_recommendation_for_added_courses(self, course_ids):
        # Filter courses by the provided topics
        topics = self.get_list_of_topics(course_ids)
        self.df = self.filter_courses_by_topics(topics)
        self.df = self.get_base_recommendations_limited(limit=200)
        
        self.df = self.df[self.df['topics'].apply(lambda x: any(topic in x for topic in topics))]
        
        course_names = self.add_courses_to_df(course_ids)
            
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

        # Initialize an empty list for storing the top courses
        top_courses = pd.DataFrame()

        # Loop over the course_ids
        for course_name in course_names:
            # Get the index of the course that matches the course_id
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
            single_course_df = self.df.iloc[course_indices].copy()

            # Compute a new score that takes into account both similarity and popularity
            # Let's give 50% importance to the similarity score and 50% to the popularity score
            single_course_df['hybrid_score'] = single_course_df['score'] * 0.5 + sim_scores[1][1] * 0.5

            # Append the DataFrame to top_courses
            top_courses = pd.concat([top_courses, single_course_df])

        # Compute a new score that takes into account both similarity and popularity
        # Let's give 50% importance to the similarity score and 50% to the popularity score
        # top_courses['hybrid_score'] = top_courses['score'] * 0.5 + sim_scores[1][1] * 0.5

        # Return the top 10 most similar courses, grouped by website and sorted by the new hybrid score
        return top_courses.groupby('website').apply(lambda x: x.sort_values('hybrid_score', ascending=False)).reset_index(drop=True)
