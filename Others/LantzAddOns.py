# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@Brief: This module implements static functions which will add param to a Hiar_Param_Tree, from a Lantz device
"""

from lantz import Feat, DictFeat, Action
from lantz import Q_
from lantz.feat import MISSING
from inspect import signature


def _mod_num_param(tree, device, feat_name, path, units='', key_widget=None):
    """
    This generates a function to modify a param on a feat changed signal
    """
    def _inner(new_val, old_val):
        """
        Change the param to new value
        """
        fattr = getattr(device, feat_name)
        if "Quantity" in str(type(new_val)):
            new_val = new_val.to(units)
            tree.addParam(path, value = new_val.magnitude, 
                          siPrefix = True, suffix = str(new_val.units))
        elif type(fattr)==str or type(fattr)==bool:
            tree.addParam(path, value = new_val)
        else:
            raise Exception
    return _inner


def _mod_num_feat(device, feat_name, units=''):
    """
    This generates a function to modify a feat on a param changed signal
    """
    def _inner(param, value):
        """
        Try to change the feat to value, if this fails, reset the param to the
        actual value of the feat.
        """
        fattr = getattr(device, feat_name)
        if "Quantity" in str(type(fattr)):
            try:
                setattr(device, feat_name, Q_(value,units))
            except Exception as e:
                param.setValue(fattr.to(units).magnitude)
                raise e
        elif type(fattr)==str or type(fattr)==bool:
            try:
                setattr(device, feat_name, value)
            except Exception as e:
                param.setValue(fattr)
                raise e
        else:
            raise Exception
    return _inner

def _buildStaticFunction(func, *args, **kwargs):
    def _inner():
        return func(*args, **kwargs)
    return _inner


def _buildKwargsFromWidgets(func, *args, **kwargs):
    def _inner():
        inputs = dict()
        for key in kwargs:
            inputs[key] = kwargs[key].value()
        return func(*args, **inputs)
    return _inner


def generateLantzParams(tree, device, group_prefix =''):
    """
    Generate a param group from a Lantz device
    """
    for fname in device.feats.keys():
        fcurrent = device.feats[fname].feat

        #Build a path
        path = '/' + device.name
        if group_prefix != '': '/' + group_prefix + path

        #Get the attr and the associated signal
        fattr = getattr(device, fname)
        fattr_changed =  getattr(device, fname+'_changed')

        #@TODO: Figure out if there is a less weird way of doing this...
        modifiers = next(fcurrent.modifiers.items())[1][MISSING]

        if type(fcurrent) == Feat:
            path += '/Feats/' + fname

            #Rebuild the limits to get a format accepted by the Spinbox widget
            bounds = modifiers['limits']
            precision = None # Right now I think, I prefer not using this to set the step size of the Spinbox, but this could be done
            if not bounds is None:
                if len(bounds) == 1: bounds = (0, bounds[0])
                if len(bounds) == 3:
                    precision = bounds[2]
                    bounds = (bounds[0], bounds[1])

            #Do thing sligthly differently for quantities than standar Python types
            if "Quantity" in str(type(fattr)):
                param = tree.addParam(path, value = fattr.magnitude, siPrefix = True, suffix = str(fattr.units), bounds=bounds)
                fattr_changed.connect(_mod_num_param(tree, device, fname, path, units = str(fattr.units)))
                tree[path].sigValueChanged.connect(_mod_num_feat(device, fname, units= str(fattr.units)))
                tree[path].setWritable(not fcurrent.read_once)
            elif not modifiers['values'] is None and type(fattr)!=bool:
                param = tree.addParam(path, value = fattr, values = list(modifiers['values'].keys()), type='list')
                fattr_changed.connect(_mod_num_param(tree, device, fname, path))
                tree[path].sigValueChanged.connect(_mod_num_feat(device, fname))
                tree[path].setWritable(not fcurrent.read_once)
            elif type(fattr)==str or type(fattr)==bool:
                tree[path] = fattr
                fattr_changed.connect(_mod_num_param(tree, device, fname, path))
                tree[path].sigValueChanged.connect(_mod_num_feat(device, fname))
                tree[path].setWritable(not fcurrent.read_once)
            else:
                print("Couldn't find the type of attribute" + fname)

        elif type(fcurrent)==DictFeat:
            path += '/DictFeats/' + fname
            if not modifiers['keys'] is None:
                param = tree.addParam(path + '/key', value = modifiers['keys'][0], values = modifiers['keys'], type='list')
                tree[path+'/value'] = fattr[modifiers['keys'][0]]
                # fattr_changed.connect(_mod_num_param(tree, device, fname, path))
                # tree[path+'/value'].sigValueChanged.connect(_mod_num_feat(device, fname))
                # tree[path+'/value'].setWritable(not fcurrent.read_once)
            else:
                print("DictFeat GUI with no keys argument not implemented yet...")



    for a_name in device.actions.keys():
        a_current = device.actions[a_name].action

        #Build a path
        path = '/' + device.name + '/Actions/' + a_name
        if group_prefix != '': '/' + group_prefix + path

        a_attr = getattr(device, a_name)

        sig = signature(a_current.func).parameters

        if type(a_current) == Action:
            
            if len(sig.keys())==1 and 'self' in sig.keys():
                tree.addParam(path, None, type='action')
                tree[path].sigActivated.connect(_buildStaticFunction(a_attr))

            else:
                kwargs = dict()
                for input_name in sig.keys():
                    if input_name != 'self':
                        tree[path+'/'+input_name] = sig[input_name].default
                        kwargs[input_name] = tree[path+'/'+input_name]
                    tree.addParam(path + '/' + "Execute", None, type='action')
                    tree[path + '/' + "Execute"].sigActivated.connect(_buildKwargsFromWidgets(a_attr, **kwargs))


