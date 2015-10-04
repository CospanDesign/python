import cmd

addresses = [
    'here@blubb.com',
    'foo@bar.com',
    'whatever@wherever.org',
]

class MyCmd(cmd.Cmd):
    def do_send(self, line):
        pass

    def complete_send(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in addresses
                if address.startswith(text)
            ]
        else:
            return addresses


if __name__ == '__main__':
    my_cmd = MyCmd()
    my_cmd.cmdloop()
