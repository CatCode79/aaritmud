# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.defer import defer

from src.commands.command_follow import command_follow


#= FUNZIONI ====================================================================

#def on_reset(bidone):
#    defer(2 , command_follow, bidone, "caldarrostaio")


def after_inject(bidone, location):
    defer(1 , command_follow, bidone, "caldarrostaio")
    #command_follow(bidone, "caldarrostaio")
