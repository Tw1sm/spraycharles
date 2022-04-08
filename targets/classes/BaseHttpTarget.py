import csv


class BaseHttpTarget:
    """
    Base class to hold output for standard HTTP spray targets
    """

    def __init__(self):
        self.username = ""
        self.password = ""

    # handle CSV out output headers. Can be customized per module
    def print_headers(self, csvfile):
        """
        Print table headers
        """
        print(
            "%-35s %-17s %-13s %-15s"
            % ("Username", "Password", "Response Code", "Response Length")
        )
        print("-" * 83)

        # create CSV file
        output = open(csvfile, "w")
        fieldnames = ["Username", "Password", "Response Code", "Response Length"]
        output_writer = csv.DictWriter(output, delimiter=",", fieldnames=fieldnames)
        output_writer.writeheader()
        output.close()

    def print_response(self, response, csvfile, timeout=False):
        """
        Handle target's response evaluation. Can be overridden per module
        """
        if timeout:
            code = "TIMEOUT"
            length = "TIMEOUT"
        else:
            code = response.status_code
            length = str(len(response.content))

        # print result to screen
        print("%-35s %-17s %13s %15s" % (self.username, self.password, code, length))

        # print to CSV file
        output = open(csvfile, "a")
        output.write(f"{self.username},{self.password},{code},{length}\n")
        output.close()
