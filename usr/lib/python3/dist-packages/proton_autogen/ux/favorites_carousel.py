from proton_autogen.ux.recent_carousel import RecentCarousel


class FavoritesCarousel(RecentCarousel):

    def set_games(self, games):

        favorites = [
            g for g in games
            if g.get("favorite", False)
        ]

        super().set_games(favorites)
