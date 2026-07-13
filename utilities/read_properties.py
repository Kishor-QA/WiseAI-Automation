import configparser
import csv

config = configparser.ConfigParser()
config.read("./config/config.ini")


class ReadConfig:

    @staticmethod
    def get_page_url():
        return config.get("login info", "Page_URL")

    @staticmethod
    def get_locator(name):
        locator = config.get("login info", name)
        parts = locator.split(',')

        locator_type = parts[0].strip()

        if locator_type == "role":
            if len(parts) == 3:
                return locator_type, parts[1].strip(), parts[2].strip()
            elif len(parts) == 2:
                return locator_type, parts[1].strip()
        elif locator_type == "css":
            return locator_type, parts[1].strip()
        elif locator_type == "text":
            return locator_type, parts[1].strip()

    @staticmethod
    def get_test_data(csv_file):
        data = []
        with open(f"./test_data/{csv_file}", mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append(row)
        return data
    
class ReadAloudCofing:
    
    @staticmethod
    def get_page_url(key="Page_URL"):
        return config.get("Read Aloud", key)

    @staticmethod
    def get_locator(name):
        locator = config.get("Read Aloud", name)
        parts = locator.split(',')

        locator_type = parts[0].strip()

        if locator_type == "role":
            if len(parts) == 3:
                return locator_type, parts[1].strip(), parts[2].strip()
            elif len(parts) == 2:
                return locator_type, parts[1].strip()
        elif locator_type == "link":
            return locator_type, parts[1].strip()
        elif locator_type == "locator":
            return locator_type, parts[1].strip()
        
        elif locator_type == "text":
            return locator_type, parts[1].strip()
        elif locator_type == "css":
            return locator_type, parts[1].strip()
        elif locator_type == "placeholder":
            return locator_type, parts[1].strip()
        elif locator_type == "role_nth":
            return locator_type, parts[1].strip(), parts[2].strip()

class UserManagamentConfig:

    @staticmethod
    def get_page_url(key="Page_URL"):
        return config.get("User Management", key)

    @staticmethod
    def get_locator(name):
        locator = config.get("User Management", name)
        parts = locator.split(',')

        locator_type = parts[0].strip()

        if locator_type == "role":
            if len(parts) == 3:
                return locator_type, parts[1].strip(), parts[2].strip()
            elif len(parts) == 2:
                return locator_type, parts[1].strip()
        elif locator_type == "link":
            return locator_type, parts[1].strip()
        elif locator_type == "text":
            return locator_type, parts[1].strip()
        elif locator_type == "css":
            return locator_type, parts[1].strip()
        
        
class ChatbotConfig:

    @staticmethod
    def get_page_url(key="Page_URL"):
        return config.get("Chatbot", key)

    @staticmethod
    def get_locator(name):
        locator = config.get("Chatbot", name)
        parts = locator.split(',')

        locator_type = parts[0].strip()

        if locator_type == "role":
            if len(parts) == 3:
                return locator_type, parts[1].strip(), parts[2].strip()
            elif len(parts) == 2:
                return locator_type, parts[1].strip()
        elif locator_type == "link":
            return locator_type, parts[1].strip()
        elif locator_type == "locator":
            return locator_type, parts[1].strip()
        
        elif locator_type == "text":
            return locator_type, parts[1].strip()
        elif locator_type == "css":
            return locator_type, parts[1].strip()
        elif locator_type == "placeholder":
            return locator_type, parts[1].strip()
        elif locator_type == "role_nth":
            return locator_type, parts[1].strip(), parts[2].strip()