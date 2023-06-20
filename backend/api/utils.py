from recipes.models import ShoppingCart


def shopping_list(user) -> str:
    header = 'Ингредиенты для рецептов:'

    purchases = ShoppingCart.objects.filter(user=user)
    recipes = [purchase.recipe for purchase in purchases]

    purchases = dict()
    for recipe in recipes:
        for component in recipe.ingredients.all():
            amount = component.amount
            ingredient = component.ingredient
            purchases[ingredient] = (purchases[ingredient] + amount
                                     if ingredient in purchases else amount)
    result = [f'{str(ingredient)} {amount} {ingredient.measurement_unit}'
              for ingredient, amount in purchases.items()]

    width = max(map(len, result))
    width = max(width, len(header))
    result = [header, '=' * width] + result + ['=' * width]
    return '\n'.join(result)
