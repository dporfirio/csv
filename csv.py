#!/usr/bin/python
'''
AUTHOR: David Porfirio

APPROACH: Modeled after a state machine with 5 possible states:
              - start of a record
              - handling of a regular field (could transition to quoted field)
              - handling a quoted field
              - handling a quote that is within a quoted field
              - handling a carriage return at the start of a record
              - handling a carriage return in a regular field
              - handling a carriage return in a quoted field
'''

import sys


def main():
    record_list = []
    field_buf = ""

    state = "RecordStart"
    ch = sys.stdin.read(1)
    while ch != '':
        if state == "RecordStart":
            if ch != '\n':
                # skip blank lines
                if ch == '"':
                    record = []
                    state = "QuotedField"
                elif ch == ',':
                    # comma at beginning required adding an empty field
                    record_list.append([])
                    record = []
                    state = "Field"
                elif ch == '\r':
                    state = "C-ReturnInStart"
                else:
                    record = []
                    field_buf += ch
                    state = "Field"
        elif state == "QuotedField":
            if ch == '"':
                state = "QuotedFieldQuote"
            elif ch == '\r':
                state = "C-ReturnInQuote"
            else:
                field_buf += ch
        elif state == "Field":
            if ch == '\n':
                record.append(field_buf)
                record_list.append(record)
                field_buf = ""
                state = "RecordStart"
            elif ch == '"':
                state = "QuotedField"
            elif ch == ',':
                record.append(field_buf)
                field_buf = ""
                state = "Field"
            elif ch == '\r':
                state = "C-ReturnInField"
            else:
                field_buf += ch
        elif state == "QuotedFieldQuote":
            if ch == '\n':
                record.append(field_buf)
                record_list.append(record)
                field_buf = ""
                state = "RecordStart"
            elif ch == '"':
                # double '"' gets processed as a single quote and added to the field
                field_buf += ch
                state = "QuotedField"
            elif ch == ',':
                record.append(field_buf)
                field_buf = ""
                state = "Field"
            elif ch == '\r':
                # \n must follow the \r, so go to Field state
                state = "Field"
        elif state == "C-ReturnInStart":
            if ch == '\n':
                # the \r is removed because it preceeds a newline
                state = "RecordStart"
            elif ch == ',':
                # comma indicates end of field, so the only char in this field is \r
                record = ['\r']
                state = "Field"
            elif ch == '\r':
                # \r is not removed, so we start the record and begin a field
                # However, the current \r still needs to be checked
                record = []
                field_buf += '\r'
                state = "C-ReturnInField"
            else:
                # \r is not removed, so we start the record and begin a field
                record = []
                field_buf += '\r' + ch
                state = "Field"
        elif state == "C-ReturnInField":
            if ch == '\n':
                # the \r is removed because it preceeds a newline
                # additionally, the newline signifies a complete record
                record.append(field_buf)
                record_list.append(record)
                field_buf = ""
                state = "RecordStart"
            elif ch == ',':
                field_buf += '\r'
                record.append(field_buf)
                field_buf = ""
                state = "Field"
            elif ch == '\r':
                # another \r means staying in the current state
                field_buf += '\r'
            else:
                field_buf += '\r' + ch
                state = "Field"
        elif state == "C-ReturnInQuote":
            if ch == '\n':
                # the \r is removed due to preceeding a newline
                field_buf += '\n'
                state = "QuotedField"
            elif ch == '"':
                field_buf += '\r'
                state = "QuotedFieldQuote"
            elif ch == '\r':
                # another \r means staying in this state
                field_buf += '\r'
            else:
                field_buf += '\r' + ch
                state = "QuotedField"

        ch = sys.stdin.read(1)

    # there may be a lingering field if EOF is encountered before a ',' or newline
    if len(field_buf) > 0:
        record.append(field_buf)
        record_list.append(record)

    print record_list


if __name__ == "__main__":
    main()
