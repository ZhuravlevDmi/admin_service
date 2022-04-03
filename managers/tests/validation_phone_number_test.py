from unittest import TestCase, main
from managers.services.functions import validation_phone_number


class ValidationPhoneNumberTest(TestCase):
    def test_plus_seven(self):
        self.assertEquals(validation_phone_number('+79213211265'), '+79213211265')

    def test_dont_seven(self):
        self.assertEquals(validation_phone_number('9213211265'), '+79213211265')

    def test_is_eight(self):
        self.assertEquals(validation_phone_number('89213211265'), '+79213211265')

    def test_seven_dont_plus(self):
        self.assertEquals(validation_phone_number('79213211265'), '+79213211265')

    def test_email_plus_number(self):
        self.assertEquals(validation_phone_number('79213211265, Dima@gmail.com'), '+79213211265')

    def test_space_number(self):
        self.assertEquals(validation_phone_number('7 914 401 4918'), '+79144014918')

    def test_email_plus_number_v2(self):
        self.assertEquals(validation_phone_number('79213211265, Dima@gmail1.com'), False)

    def test_lack_of_numbers(self):
        self.assertEquals(validation_phone_number('7921321126'), False)

    def test_enumeration_of_numbers(self):
        self.assertEquals(validation_phone_number('792133421126'), False)

    def test_wrong_number(self):
        self.assertEquals(validation_phone_number('8234954749'), False)


if __name__ == '__main__':
    main()
