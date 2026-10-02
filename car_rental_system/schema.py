from drf_spectacular.openapi import AutoSchema


class CustomAutoSchema(AutoSchema):

    def get_tags(self):
        path = self.path

        # Authentication and user management
        if path.startswith("/api/accounts/"):
            return ["Accounts & Authentication"]

        # Cars and categories
        if path.startswith("/api/cars/"):
            return ["Cars & Categories"]

        # Rentals
        if path.startswith("/api/rentals/rentals/"):
            return ["Rentals"]

        # Payments
        if path.startswith("/api/rentals/payments/"):
            return ["Payments"]

        # Reviews
        if path.startswith("/api/rentals/reviews/"):
            return ["Reviews"]

        return ["Other"]