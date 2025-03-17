import requests


class ZoomAPI:
    def __init__(self, access_token: str, account_id: str = "me"):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://api.zoom.us/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_account_id_by_email(self, email):
        """
        Получает `account_id` по email (логину) пользователя.
        """
        url = f"{self.base_url}/users/{email}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("id"), data.get("email")

    def get_sub_accounts(self):
        """
        Возвращает список дочерних аккаунтов головного аккаунта.
        """
        sub_accounts = []
        next_page_token = None
        page_size = 100

        while True:
            params = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token

            url = f"{self.base_url}/accounts"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            sub_accounts.extend(data.get("accounts", []))

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

        return [(acc["id"], acc.get("email", "Unknown")) for acc in sub_accounts]

    def is_user_id(self, user_id):
        """
        Проверяет, является ли переданный ID пользователем (user_id), а не аккаунтом.
        """
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

    def get_recordings_for_accounts(self, accounts_list):
        """
        Получает записи для списка переданных аккаунтов или пользователей.
        """
        all_recordings = []
        for acc_id, email in accounts_list:
            next_page_token = None
            page_size = 300
            endpoint = "users" if self.is_user_id(acc_id) else "accounts"

            while True:
                params = {"page_size": page_size}
                if next_page_token:
                    params["next_page_token"] = next_page_token

                url = f"{self.base_url}/{endpoint}/{acc_id}/recordings"
                response = requests.get(url=url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                for meeting in data.get("meetings", []):
                    recording_files = meeting.get("recording_files", [])
                    for file in recording_files:
                        file_size = file.get("file_size", 0) / (1024 * 1024)  # Преобразуем байты в мегабайты
                        if "shared_screen_with_speaker_view" in file.get("recording_type", "").lower() and file_size >= 10:
                            all_recordings.append({
                                "topic": meeting.get("topic"),
                                "download_url": file.get("download_url"),
                                "meeting_id": meeting.get("id"),
                                "start_time": meeting.get("start_time"),
                                "duration": meeting.get("duration"),
                                "host_email": email,
                                "file_size_mb": round(file_size, 2)
                            })

                next_page_token = data.get("next_page_token")
                if not next_page_token:
                    break

        return all_recordings

    def get_all_recordings(self, accounts_list=None):
        """
        Получает список всех записей, используя переданный список аккаунтов (ID или email).
        Если аккаунты не переданы, автоматически получает список дочерних аккаунтов.
        """
        if accounts_list is None:
            accounts_list = [(self.account_id, "Unknown")] + self.get_sub_accounts()
        else:
            accounts_list = [self.get_account_id_by_email(acc) if "@" in acc else (acc, "Unknown") for acc in accounts_list]

        return self.get_recordings_for_accounts(accounts_list)

    def print_recordings_info(self, recordings):
        """
        Выводит список записей с названием, ссылкой на загрузку и логином владельца.
        """
        for rec in recordings:
            print(f"Title: {rec['topic']}, Download URL: {rec['download_url']}, Host Email: {rec['host_email']}, Start Time: {rec['start_time']}, Duration: {rec['duration']} min, File Size: {rec['file_size_mb']} MB")
