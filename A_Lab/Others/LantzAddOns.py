# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@Brief: This module implements static functions which will add param to a Hiar_Param_Tree, from a Lantz device
"""

from lantz import Feat, DictFeat, Action, Q_
from lantz.feat import MISSING, _dget
from lantz.ui.widgets import DictFeatWidget, FeatWidget, connect_feat, MagnitudeMixin, register_wrapper, WidgetMixin
from inspect import signature

from pyqtgraph.parametertree.Parameter import Parameter, registerParameterType
from pyqtgraph.parametertree.parameterTypes import WidgetParameterItem
from pyqtgraph.parametertree.ParameterItem import ParameterItem
import pyqtgraph as pg
from decimal import Decimal as D
from pyqtgraph.python2_3 import asUnicode

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core


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
    registerParameterType('feats', FeatParameter, override=True)
    registerParameterType('dictfeats', DictFeatParameter, override=True)
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

            skip = False
            # if "Quantity" in str(type(fattr)): value = fattr.magnitude
            # else: value = fattr
            value = fattr

            feat = device.feats[fname]
            if not skip:
                tree.addParam(path, value = value, feat = feat, type='feats', target = device)
                w = list(tree[path].items)[0].widget
                connect_feat(w, device, feat_name=fname)
                try:
                    w.setValue(feat.instance.recall(fname))
                except:
                    pass

        elif type(fcurrent)==DictFeat:
            path += '/DictFeats/' + fname

            skip = False
            feat = device.feats[fname]
            df = feat.feat
            key = _dget(df.modifiers, device, fname)['keys'][0]
            value = fattr[key]
            # if "Quantity" in str(type(value)): value = value.magnitude
            # else: value = value

            if not skip:
                tree.addParam(path, value=value, feat=feat, type='dictfeats', target=device)
                w = list(tree[path].items)[0].widget
                #connect_feat(w, device, feat_name=fname)
                #w.setValue(feat.instance.recall(fname))



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



##-------------------------------------------------------------------------------------
#           Parameter and ParameterItems making use of custom pg_FeatWidget and pg_DictFeatWidget
##-------------------------------------------------------------------------------------

class FeatParameterItem(WidgetParameterItem):
    """
    Lantz Feat param
    """
    useCustom = True

    def __init__(self, param, depth):
        self.targetValue = None
        WidgetParameterItem.__init__(self, param, depth)

    def makeWidget(self):
        opts = self.param.opts
        feat = opts['feat']

        w = pg_FeatWidget(self.parent(), **opts)
        w.setMaximumHeight(20)  ## set to match height of spin box and line edit
        self.widget = w

        if feat.values and set(feat.values) == {True, False}:
            self.hideWidget = False
        return w

    def valueChanged(self, param, val, force=False):
        ## Little hack to make sure self.widgetValueChanged is connected otherwise we might get an error when disconnecting
        try:
            self.widget.sigChanged.connect(self.widgetValueChanged)
        finally:
            super().valueChanged(param, val, force=False)


class DictFeatParameterItem(WidgetParameterItem):
    """
    Lantz Feat param

    """
    def __init__(self, param, depth):
        self.targetValue = None
        WidgetParameterItem.__init__(self, param, depth)


    def makeWidget(self):
        opts = self.param.opts

        #w = DictFeatWidget(parent=self.parent(), target=opts['target'], feat=opts['feat'])
        w = pg_DictFeatWidget(parent=self.parent(), **opts)

        w.sigChanged = w._value_widget.valueChanged

        #w.setMaximumHeight(20)  ## set to match height of spin box and line edit

        self.widget = w  ## needs to be set before limits are changed
        self.hideWidget = False
        return w

    def valueChanged(self, param, val, force=False):
        ## Little hack to make sure self.widgetValueChanged is connected otherwise we might get an error when disconnecting
        try:
            self.widget.sigChanged.connect(self.widgetValueChanged)
        finally:
            super().valueChanged(param, val, force=force)

class FeatParameter(Parameter):
    itemClass = FeatParameterItem

    def __init__(self, **opts):
        Parameter.__init__(self, **opts)

class DictFeatParameter(Parameter):
    itemClass = DictFeatParameterItem

    def __init__(self, **opts):
        Parameter.__init__(self, **opts)


##-------------------------------------------------------------------------------------
#           Modified Spinbox to work with the Lantz framework
##-------------------------------------------------------------------------------------

class pgSpinBox(pg.SpinBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sigChanged = self.valueChanged


    def setSuffix(self, suffix):
        # remove the space added by lantz
        super().setSuffix(suffix[1:])

    def f(self, value):
        print(value)


@register_wrapper
class pgSpinbox_WidgetMixin(MagnitudeMixin):
    _WRAPPED = (pgSpinBox, pg.SpinBox)

    def setValue(self, value=MISSING, **kwargs):
        if value is MISSING:
            font = _gui.QFont()
            font.setItalic(True)
            self.setFont(font)
        elif isinstance(value, Q_):
            super().setValue(value.to(self._units).magnitude)
        else:
            super().setValue(value)


##-------------------------------------------------------------------------------------
#           Modified FeatWidget and DictFeatWidget to work with the pyqtgraph framework
##-------------------------------------------------------------------------------------

class pg_FeatWidget(object):

    def __new__(cls, parent, target, feat, value, **opts):
        """
        :param parent: parent widget.
        :param target: driver object to connect.
        :param feat: Feat to connect.
        """

        isQuantity = lambda x: 'Quantity' in str(type(value))
        isInt = lambda x: int == type(value)
        if (isInt(feat) or isQuantity(feat)):
            defs = {
                'value': 0, 'min': None, 'max': None, 'int': isInt(feat),
                'step': 1.0, 'minStep': 1.0, 'dec': not isInt(feat),
                'siPrefix': not isInt(feat), 'suffix': ''
            }
            defs.update(opts)
            if 'limits' in opts:
                defs['bounds'] = opts['limits']
            w = pgSpinBox()
            w.setOpts(**defs)
            w.sigChanged = w.sigValueChanged
            w.sigChanging = w.sigValueChanging

            # Wrap with lantz
            pgSpinbox_WidgetMixin.wrap(w)
            w.bind_feat(feat)
            w.lantz_target = target
        else:
            w = FeatWidget(parent, target, feat)
            w.sigChanged = w.valueChanged

        return w

class pg_DictFeatWidget(DictFeatWidget):
    """Widget to show a DictFeat.

    :param parent: parent widget.
    :param target: driver object to connect.
    :param feat: DictFeat to connect.
    """

    def __init__(self, parent, target, feat, **opts):
        _gui.QWidget.__init__(self,parent)
        self._feat = feat

        layout = _gui.QHBoxLayout(self)

        if feat.keys:
            wid = _gui.QComboBox()
            if isinstance(feat.keys, dict):
                self._keys = list(feat.keys.keys())
            else:
                self._keys = list(feat.keys)

            wid.addItems([str(key) for key in self._keys])
            wid.currentIndexChanged.connect(self._combobox_changed)
        else:
            wid = _gui.QLineEdit()
            wid.textChanged.connect(self._lineedit_changed)

        layout.addWidget(wid)
        self._key_widget = wid

        wid = pg_FeatWidget(parent, target, feat, **opts)
        wid.feat_key = self._keys[0]
        wid.lantz_target = target

        wid.feat_key = self._keys[0]
        layout.addWidget(wid)

        #self.sigChanged = wid.sigChanged
        #self.sigChanging = wid.sigChanging

        self._value_widget = wid

    @_core.Slot(int, object, object)
    def _combobox_changed(self, value, old_value=MISSING, other=MISSING):
        super()._combobox_changed(value, old_value=old_value, other=other)
        self._value_widget.on_feat_value_changed(self._feat.get_cache(self._value_widget.lanz_target, key=self._value_widget.feat_key), other={'key':self._value_widget.feat_key})


