from app.enums import ReactionType


def calculate_expected_score(rating_a, rating_b):
    """
    Calculate expected score using logistic curve

    Args:
        rating_a: Rating of person being swiped on
        rating_b: Rating of person doing the swiping

    Returns:
        Float between 0 and 1 representing expected probability
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def get_new_rating(user_rating, swiper_rating, reaction_type: ReactionType):
    """
    Update rating based on swipe interaction

    Args:
        user_rating: Current rating of user being swiped on
        swiper_rating: Rating of person doing the swiping
        reaction_type: Type of reaction (like or dislike)

    Returns:
        New rating for the user being swiped on
    """
    actual_score = 1 if reaction_type == ReactionType.like else 0
    expected_score = calculate_expected_score(
        user_rating, swiper_rating)

    k_factor = 32
    rating_change = k_factor * (actual_score - expected_score)

    return user_rating + rating_change
