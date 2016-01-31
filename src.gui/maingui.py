# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.ICONIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_filePickerFileRead = wx.FilePickerCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.Size( -1,-1 ), wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN )
		bSizer2.Add( self.m_filePickerFileRead, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_checkBoxLoadLast = wx.CheckBox( self.m_panel1, wx.ID_ANY, u"Load last file on start", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_checkBoxLoadLast, 0, wx.ALL, 5 )
		
		self.m_staticline7 = wx.StaticLine( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer2.Add( self.m_staticline7, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText5 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"CRC in File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		bSizer9.Add( self.m_staticText5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlCRCOld = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		bSizer9.Add( self.m_textCtrlCRCOld, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText6 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Calculated CRC", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		bSizer9.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlCRCNew = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		bSizer9.Add( self.m_textCtrlCRCNew, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer2.Add( bSizer9, 0, wx.EXPAND, 5 )
		
		self.m_staticline71 = wx.StaticLine( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer2.Add( self.m_staticline71, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_buttonReCalculate = wx.Button( self.m_panel1, wx.ID_ANY, u"&Re-Calculate", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_buttonReCalculate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer18.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_buttonSave = wx.Button( self.m_panel1, wx.ID_ANY, u"&Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_buttonSave, 0, wx.ALL, 5 )
		
		self.m_buttonSaveAs = wx.Button( self.m_panel1, wx.ID_ANY, u"Save &As ...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_buttonSaveAs, 0, wx.ALL, 5 )
		
		
		bSizer18.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_buttonAboutDialog = wx.Button( self.m_panel1, wx.ID_ANY, u"About ...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_buttonAboutDialog, 0, wx.ALL, 5 )
		
		
		bSizer2.Add( bSizer18, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		self.m_panel1.SetSizer( bSizer2 )
		self.m_panel1.Layout()
		bSizer2.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItemAboutDialog = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"&About ...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItemAboutDialog )
		
		self.m_menubar1.Append( self.m_menu1, u"&Help" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.m_toolAboutDialog = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"About ...", wx.ArtProvider.GetBitmap( u"priv/icons/information.png", wx.ART_OTHER ), wx.NullBitmap, wx.ITEM_NORMAL, u"About ...", u"Show the About Dialog", None ) 
		
		self.m_toolBar1.Realize() 
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_notebookAbout = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panelAbout = wx.Panel( self.m_notebookAbout, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer10 = wx.BoxSizer( wx.VERTICAL )
		
		
		bSizer10.AddSpacer( ( 0, 0), 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticTextAppNameVersion = wx.StaticText( self.m_panelAbout, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_staticTextAppNameVersion.Wrap( -1 )
		bSizer10.Add( self.m_staticTextAppNameVersion, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticTextCopyright = wx.StaticText( self.m_panelAbout, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_staticTextCopyright.Wrap( -1 )
		bSizer10.Add( self.m_staticTextCopyright, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_hyperlinkURL = wx.HyperlinkCtrl( self.m_panelAbout, wx.ID_ANY, u"wxFB Website", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_ALIGN_CENTRE|wx.HL_DEFAULT_STYLE )
		bSizer10.Add( self.m_hyperlinkURL, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer10.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.m_panelAbout.SetSizer( bSizer10 )
		self.m_panelAbout.Layout()
		bSizer10.Fit( self.m_panelAbout )
		self.m_notebookAbout.AddPage( self.m_panelAbout, u"About", True )
		
		bSizer8.Add( self.m_notebookAbout, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.m_buttonClose = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer8.Add( self.m_buttonClose, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.SetSizer( bSizer8 )
		self.Layout()
		bSizer8.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class PanelAboutDocument
###########################################################################

class PanelAboutDocument ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )
		
		bSizer111 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_textCtrlDocument = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer111.Add( self.m_textCtrlDocument, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer111 )
		self.Layout()
		bSizer111.Fit( self )
	
	def __del__( self ):
		pass
	

