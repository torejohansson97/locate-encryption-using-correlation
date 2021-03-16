#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: capture
# GNU Radio version: 3.8.1.0
# Modified: torej 2021-03-16

import ctypes
import sys

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import sys

from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd

from gnuradio import qtgui

class capture(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "capture")
        
        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 5000000
        self.freq = freq = 2.4e9 + 128e6

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("addr=192.168.10.2", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(30, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(32, True)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, '../data/ofile', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_am_demod_cf_0 = analog.am_demod_cf(
        	channel_rate=samp_rate,
        	audio_decim=1,
        	audio_pass=1.2e6,
        	audio_stop=1.6e6,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_am_demod_cf_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.analog_am_demod_cf_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "capture")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)