from common.routing import navigation, page_config


def main():
    initialize()
    # process_data()
    # finalize()


def initialize():
    # print("Initializing...")
    page_config()
    navigation()


def process_data():
    print("Processing data...")


def finalize():
    print("Finalizing...")


if __name__ == "__main__":
    main()
