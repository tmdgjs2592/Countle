

def calculate_similarity(word, country, model):
    try:
        similarity = model.similarity(word, country)
        return similarity
    except KeyError as e:
        return None  # Return None if the word or country is not in the model's vocabulary