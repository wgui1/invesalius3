import wx
import wx.gizmos as gizmos
import wx.lib.pubsub as ps
import wx.lib.splitter as spl

import dicom_preview_panel as dpp

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.Point(5, 5),
                          size=wx.Size(280, 656))
        
        sizer = wx.BoxSizer(wx.VERTICAL)        
        sizer.Add(InnerPanel(self), 1, wx.EXPAND|wx.GROW|wx.ALL, 5)
        self.SetSizer(sizer)

# Inner fold panel
class InnerPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.Point(5, 5),
                          size=wx.Size(680, 656))
        
        splitter = spl.MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetOrientation(wx.VERTICAL)
        self.splitter = splitter
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.text_panel = TextPanel(splitter)
        splitter.AppendWindow(self.text_panel, 250)
        
        self.image_panel = ImagePanel(splitter)
        splitter.AppendWindow(self.image_panel, 250)
        
        self.__bind_evt()
        
    def __bind_evt(self):
        ps.Publisher().subscribe(self.ShowDicomPreview, "Load import panel")
        
    def ShowDicomPreview(self, pubsub_evt):
        dicom_groups = pubsub_evt.data
        self.text_panel.Populate(dicom_groups)
        
        
class TextPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour((255,0,0))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        
        tree = gizmos.TreeListCtrl(self, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        | wx.TR_HIDE_ROOT
                                        | wx.TR_ROW_LINES
                                        | wx.TR_COLUMN_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                        | wx.TR_SINGLE
                                        )
                                   
                                   
        tree.AddColumn("Patient name")
        tree.AddColumn("Patient ID")
        tree.AddColumn("Age")
        tree.AddColumn("Gender")
        tree.AddColumn("Study description")
        tree.AddColumn("Modality")
        tree.AddColumn("Date acquired")
        tree.AddColumn("# Images")
        tree.AddColumn("Institution")
        tree.AddColumn("Date of birth")
        tree.AddColumn("Accession Number")
        tree.AddColumn("Referring physician")

        tree.SetMainColumn(0)        # the one with the tree in it...
        tree.SetColumnWidth(0, 280)  # Patient name
        tree.SetColumnWidth(1, 110)  # Patient ID
        tree.SetColumnWidth(2, 40)   # Age
        tree.SetColumnWidth(3, 60)   # Gender
        tree.SetColumnWidth(4, 160)  # Study description
        tree.SetColumnWidth(5, 70)   # Modality
        tree.SetColumnWidth(6, 200)  # Date acquired
        tree.SetColumnWidth(7, 70)   # Number Images
        tree.SetColumnWidth(8, 130)  # Institution
        tree.SetColumnWidth(9, 100)  # Date of birth
        tree.SetColumnWidth(10, 140) # Accession Number
        tree.SetColumnWidth(11, 160) # Referring physician

        self.root = tree.AddRoot("InVesalius Database")
        self.tree = tree

    def Populate(self, patient_list):
        tree = self.tree

        for patient in patient_list:
            ngroups = patient.ngroups
            dicom = patient.GetDicomSample()
            title = dicom.patient.name + " (%d series)"%(ngroups)
            date_time = "%s %s"%(dicom.acquisition.date,
                                 dicom.acquisition.time)

            parent = tree.AppendItem(self.root, title)
            
            tree.SetItemText(parent, str(dicom.patient.id), 1)
            tree.SetItemText(parent, str(dicom.patient.age), 2)
            tree.SetItemText(parent, str(dicom.patient.gender), 3)
            tree.SetItemText(parent, str(dicom.acquisition.study_description), 4)
            tree.SetItemText(parent, str(dicom.acquisition.modality), 5)
            tree.SetItemText(parent, str(date_time), 6)
            tree.SetItemText(parent, str(patient.nslices), 7)
            tree.SetItemText(parent, str(dicom.acquisition.institution), 8)
            tree.SetItemText(parent, str(dicom.patient.birthdate), 9)
            tree.SetItemText(parent, str(dicom.acquisition.accession_number), 10)
            tree.SetItemText(parent, str(dicom.patient.physician), 11)

            group_list = patient.GetGroups()
            for group in group_list:
                dicom = group.GetDicomSample()

                child = tree.AppendItem(parent, group.title)
                tree.SetItemPyData(child, group)

                tree.SetItemText(child, str(group.title), 0)
                tree.SetItemText(child, str(dicom.acquisition.protocol_name), 4)
                tree.SetItemText(child, str(dicom.acquisition.modality), 5)
                tree.SetItemText(child, str(date_time), 6)
                tree.SetItemText(child, str(group.nslices), 7)

        tree.Expand(self.root)
        
        tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)

    def OnActivate(self, evt):
        print "OnActivate"
        item = evt.GetItem()
        group = self.tree.GetItemPyData(item)
        if group:
            print "send"
            ps.Publisher().sendMessage('Open DICOM group',
                                        group)

        else:
            if self.tree.IsExpanded(item):
                self.tree.Collapse(item)
            else:
                self.tree.Expand(item)

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())
        
class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        #self.SetBackgroundColour((0,255,0))
        
        splitter = spl.MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        splitter.SetOrientation(wx.HORIZONTAL)
        self.splitter = splitter
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.text_panel = SeriesPanel(splitter)
        splitter.AppendWindow(self.text_panel, 600)
        
        self.image_panel = SlicePanel(splitter)
        splitter.AppendWindow(self.image_panel, 250)
        
class SeriesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        #self.SetBackgroundColour((0,0,0)) 

        self.serie_preview = dpp.DicomPreviewSeries(self)
        self.dicom_preview = dpp.DicomPreview(self)
        self.dicom_preview.Show(0)
       
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.serie_preview, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.dicom_preview, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Fit(self)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)        
        self.Show()


        self.__bind_evt()
        self._bind_gui_evt()

    def __bind_evt(self):
        ps.Publisher().subscribe(self.ShowDicomSeries, "Load dicom preview")

    def _bind_gui_evt(self):
        self.Bind(dpp.EVT_SELECT_SERIE, self.OnSelectSerie)

    def OnSelectSerie(self, evt):
        serie = evt.GetSelectID()
        self.dicom_preview.SetDicomSerie(serie)

        self.dicom_preview.Show(1)
        #self.sizer.Detach(self.serie_preview)
        self.serie_preview.Show(0)
        self.sizer.Layout()
        #self.Show()
        self.Update()


    def ShowDicomSeries(self, pubsub_evt):
        print "---- ShowDicomSeries ----"
        first_patient = pubsub_evt.data
        self.serie_preview.SetPatientGroups(first_patient)
        self.dicom_preview.SetPatientGroups(first_patient)
        


class SlicePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour((255,255,255))
