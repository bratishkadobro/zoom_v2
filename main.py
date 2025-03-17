from utils import zoom

if __name__ == "__main__":
    from config import API_KEY # access token, полученный с помощью отдельного веб-сервера
    access_token = API_KEY
    account_id = "me" # по умолчанию, указывает на текущий головной аккаунт

    fetcher = zoom.ZoomAPI(access_token, account_id)
    
    accounts_list = ["esokolov@hse.ru"] # список аккаунтов для выгрузки
    #TODO: Дать возможность вносить аккаунты через веб-приложение
    recordings = fetcher.get_all_recordings(accounts_list)
    
    
    fetcher.print_recordings_info(recordings)
    print(f"\nTotal recordings found: {len(recordings)}")