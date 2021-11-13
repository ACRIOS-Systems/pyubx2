"""
Exception handling tests for UBXMessage constructor and parse

Created on 3 Oct 2020

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""
# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

import unittest

from pyubx2 import (
    UBXMessage,
    UBXReader,
    UBXTypeError,
    UBXParseError,
    UBXMessageError,
    UBXStreamError,
    GET,
    SET,
    POLL,
    VALCKSUM,
)


class ExceptionTest(unittest.TestCase):
    def setUp(self):
        self.bad_hdr = b"\xb0b\x05\x01\x02\x00\x06\x01\x0f\x38"
        self.bad_len = b"\xb5b\x05\x01\x03\x00\x06\x01\x0f\x37"
        self.bad_msg = b"\xb5b\x66\x66\x02\x00\x06\x01\xd5\x77"
        self.mga_ini = b"\xb5b\x13\x40\x14\x00\x01\x00\x01\x02\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x93\xc8"
        self.maxDiff = None

    def tearDown(self):
        pass

    def testInvMode(self):  # test invalid mode
        EXPECTED_ERROR = "Invalid msgmode 3 - must be 0, 1 or 2"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("CFG", "CFG-MSG", 3, msgClass=240, msgID=5)

    def testAckCkT(self):  # bad checksum
        EXPECTED_ERROR = "Message checksum (.*) invalid - should be (.*)"
        ack_ack_badck = b"\xb5b\x05\x01\x02\x00\x06\x01\x0f\x37"
        with self.assertRaisesRegex(UBXParseError, EXPECTED_ERROR):
            UBXReader.parse(ack_ack_badck, validate=VALCKSUM)

    def testFill_CFGNMEA(self):  # incorrect type (integer not binary)
        EXPECTED_ERROR = (
            # "Incorrect type for attribute 'filter' in SET message class CFG-NMEA"
            "Incorrect type for attribute 'nmeaVersion' in SET message class CFG-NMEA"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG", "CFG-NMEA", SET, filter=45, nmeaVersion="xx", numSV=4, flags=14
            )

    def testFill_CFGDAT(self):  # incorrect type (string not integer)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'majA' in SET message class CFG-DAT"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG", "CFG-DAT", SET, majA="xcy", flat="xyx", dX="xyz", dY="xyx"
            )

    def testFill_CFGDAT2(self):  # incorrect type (integer not string)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'majA' in SET message class CFG-DAT"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG", "CFG-DAT", SET, majA="xcy", flat="xyx", dX="xyz", dY="xyx"
            )

        # def testFill_CFGDAT3(self):  # incorrect type (signed not unsigned integer)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'datumNum' in GET message class CFG-DAT"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG",
                "CFG-DAT",
                GET,
                datumNum="xyz",
                majA=123.45,
                flat=123.45,
                dX=123.45,
                dY=123.45,
            )

    def testFill_CFGDAT4(self):  # incorrect type (string not float)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'majA' in GET message class CFG-DAT"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG",
                "CFG-DAT",
                GET,
                datumNum=4,
                datumName=b"WGS84",
                majA="xxx",
                flat=123.45,
                dX=123.45,
                dY=123.45,
            )

    def testFill_CFGDAT5(self):  # incorrect type (binary not float)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'flat' in GET message class CFG-DAT"
        )
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage(
                "CFG",
                "CFG-DAT",
                GET,
                datumNum=4,
                datumName=b"WGS84",
                majA=123.45,
                flat=b"\xffffff",
                dX=123.45,
                dY=123.45,
            )

    def testFill_XXX(self):  # test for invalid message type
        EXPECTED_ERROR = "Undefined message, class XXX, id XXX-YYY"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("XXX", "XXX-YYY", POLL)

    def testParseBadHdr(self):  # test for invalid message header in bytes
        EXPECTED_ERROR = "Invalid message header (.*) - should be (.*)"
        with self.assertRaisesRegex(UBXParseError, EXPECTED_ERROR):
            UBXReader.parse(self.bad_hdr)

    def testParseBadLen(self):  # test for invalid message length in bytes
        EXPECTED_ERROR = "Invalid payload length (.*) - should be (.*)"
        with self.assertRaisesRegex(UBXParseError, EXPECTED_ERROR):
            UBXReader.parse(self.bad_len)

    def testFill_NONEXISTCLS(self):  # non existent message class
        EXPECTED_ERROR = "Undefined message, class XXX, id XXX-YYY"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage(
                "XXX", "XXX-YYY", SET, filter=45, nmeaVersion="xx", numSV=4, flags=14
            )

    def testFill_NONEXISTID(self):  # non existent message id
        EXPECTED_ERROR = "Undefined message, class CFG, id CFG-XXX"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage(
                "CFG", "CFG-XXX", SET, filter=45, nmeaVersion="xx", numSV=4, flags=14
            )

    def testFill_INVALIDATTR(self):  # test invalid attribute type with provided values
        EXPECTED_ERROR = "Unknown attribute type Z2"
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage("FOO", "FOO-BAR", GET, spam=45, eggs="xx")

    def testFill_INVALIDATTR2(
        self,
    ):  # test invalid attribute type with defaulted values
        EXPECTED_ERROR = "Unknown attribute type Z2"
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXMessage("FOO", "FOO-BAR", GET, eggs=45)

    def testParse_INVALIDATTR(self):  # test for invalid message header in bytes
        EXPECTED_ERROR = "Unknown attribute type Z2"
        with self.assertRaisesRegex(UBXTypeError, EXPECTED_ERROR):
            UBXReader.parse(self.bad_msg)

    def testImmutability(self):  # verify object is immutable after instantiation
        EXPECTED_ERROR = "Object is immutable. Updates to msgClass not permitted after initialisation."
        res = UBXMessage("CFG", "CFG-MSG", POLL, msgClass=240, msgID=5)
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            res.msgClass = 222

    def testBadCfgValSet(self):  # test for invalid cfgData keyname
        EXPECTED_ERROR = "Undefined configuration database key FOO_BAR"
        cfgData = [("FOO_BAR", 9600)]
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage.config_set(0, 0, cfgData)

    def testBadCfgKey(self):  # test for invalid key
        EXPECTED_ERROR = "Undefined configuration database key 0x11223344"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage.cfgkey2name(0x11223344)

    def testMaxConfigSet(self):  # test for >64 configuration tuples
        EXPECTED_ERROR = "Number of configuration tuples 65 exceeds maximum of 64"
        cfgData = []
        for i in range(65):
            cfgData.append(("CFG_TEST", i))
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage.config_set(0, 0, cfgData)

    def testMaxConfigDel(self):  # test for >64 configuration keys
        EXPECTED_ERROR = "Number of configuration keys 68 exceeds maximum of 64"
        keys = ["CFG_TEST"] * 68
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage.config_del(0, 0, keys)

    def testMaxConfigPoll(self):  # test for >64 configuration keys
        EXPECTED_ERROR = "Number of configuration keys 67 exceeds maximum of 64"
        keys = ["CFG_TEST"] * 67
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage.config_poll(0, 0, keys)

    def testFill_MGASET(
        self,
    ):  #  test MGA-PMREQ SET constructor without payload keyword
        EXPECTED_ERROR = "MGA message definitions must include type or payload keyword"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage(b"\x13", b"\x03", SET, a0UTC=15, wnRec=23, wnLSF=41)

    def testFill_RXMPMREQSET3(
        self,
    ):  #  test RXM-PMREQ SET constructor without version or payload keyword
        EXPECTED_ERROR = (
            "RXM-PMREQ message definitions must include version or payload keyword"
        )
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage(
                "RXM", "RXM-PMREQ", SET, duration=67305985, flags=b"\x01\x02\x03\x04"
            )

    def testFill_RXMPMPGET(
        self,
    ):  #  test RXM-PMP GET constructor without version or payload keyword
        EXPECTED_ERROR = (
            "RXM-PMP message definitions must include version or payload keyword"
        )
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("RXM", "RXM-PMP", GET, timeTag=0)

    def testFill_RXMRLMGET(
        self,
    ):  #  test RXM-RLM GET constructor without type or payload keyword
        EXPECTED_ERROR = (
            "RXM-RLM message definitions must include type or payload keyword"
        )
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("RXM", "RXM-RLM", GET, version=0, svId=23)

    def testFill_CFGNMEAGET(
        self,
    ):  #  test CFG-NMEA GET constructor without payload keyword
        EXPECTED_ERROR = "CFG-NMEA message definitions must include payload keyword"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("CFG", "CFG-NMEA", GET, filter=0, nmeaVerson=64)

    def testFill_CFGVALGET1(
        self,
    ):  #  test CFG-VALGET GET constructor without payload keyword
        EXPECTED_ERROR = "CFG-VALGET message definitions must include payload keyword"
        with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
            UBXMessage("CFG", "CFG-VALGET", GET, version=0, layer=0)

    def testParseMode(self):  # test invalid parse message mode
        EXPECTED_ERROR = "Invalid message mode 3 - must be 0, 1 or 2"
        with self.assertRaisesRegex(UBXParseError, EXPECTED_ERROR):
            UBXReader.parse(
                b"\xb5b\x05\x01\x02\x00\x06\x01\x0f\x38", validate=VALCKSUM, msgmode=3
            )

    def testParseMode2(self):  # test parser with incorrect mode for input message
        EXPECTED_ERROR = "Unknown message type clsid (.*), msgid (.*), mode GET"
        with self.assertRaisesRegex(UBXParseError, EXPECTED_ERROR):
            UBXReader.parse(self.mga_ini, validate=VALCKSUM)

    def testStreamMode(self):  # test invalid stream message mode
        EXPECTED_ERROR = "Invalid stream mode 3 - must be 0, 1 or 2"
        with self.assertRaisesRegex(UBXStreamError, EXPECTED_ERROR):
            UBXReader(None, validate=VALCKSUM, msgmode=3)

#     # can only be tested by temporarily removing a valid message definition
#     def testIdentity(self):  # test for invalid message identity
#         EXPECTED_ERROR = "Unknown UBX message type class {'b\x77'} id {'b\x88'}"
#         msg = UBXMessage('b\x77', 'b\x88', POLL)
#         with self.assertRaisesRegex(UBXMessageError, EXPECTED_ERROR):
#             msg.identity()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
