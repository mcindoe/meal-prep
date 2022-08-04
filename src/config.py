import yaml

from mealprep.src.constants import ConfigEntries


class Config:
    def __init__(self):
        with open("/home/conor/Programming/mealprep/config.yaml", "r") as fp:
            self.config = yaml.load(fp, yaml.SafeLoader)

    def get_email_addresses(self):
        return self.config[ConfigEntries.EMAIL_ADDRESSES.value]

