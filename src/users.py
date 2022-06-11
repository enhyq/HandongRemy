
class Users:

    # key   : kakao_id
    # value : {'id' : value, 'pw' : value, 'student_id' : value, 'session' : value}
    user_data = {}

    def is_user_registered(self, kakao_id) -> bool:
        for existing_id in self.user_data.keys():
            if kakao_id == existing_id:
                return True
        return False

    def get_user_data(self, kakao_id) -> dict:
        if self.is_user_registered(kakao_id):
            return self.user_data[kakao_id]
        return {}