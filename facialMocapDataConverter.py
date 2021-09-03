from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import csv
import os
import pprint
iconPath = os.path.join(os.path.dirname(__file__),'icon')
manualPath = os.path.join(os.path.dirname(__file__),'manual')
def refreshNS(*args):
    nsLst = [i for i in cmds.namespaceInfo(lon=True) if not 'UI' in i and not 'shared' in i]
    
    for item in cmds.optionMenu('nameSpaceMenu', q=True, ill=True) or []:
        cmds.deleteUI(item)

    for ns in nsLst:        
        cmds.menuItem(ns,l=ns,p='nameSpaceMenu')
            
        

def DeleteKey(myVal, _ignore):

    # Delete key
    blendShapeNode = cmds.textFieldButtonGrp('blNodeField',q=True,tx=True)
    if not blendShapeNode:
        blendShapeNode = 'asARKit'
    ns = cmds.optionMenu('nameSpaceMenu',v=True,q=True)    
    if ns:
        blendShapeNode = '%s:%s' % (ns,blendShapeNode)
    if cmds.objectType(blendShapeNode) == 'transform':  
        attrLst = cmds.listAttr(blendShapeNode,keyable=True)
    else:    
        attrLst = cmds.listAttr('%s.w' % blendShapeNode,m=True)
    for attr in attrLst:
        cmds.cutKey('%s.%s' % (blendShapeNode,attr))
        cmds.setAttr('%s.%s' % (blendShapeNode,attr),0)

def OpenDir(myVal, _ignore):    
    path = cmds.fileDialog2(dir= "c:/", dialogStyle=2, fm=1, ff="*.csv")    
    if not path:
        return
    path2 = path[0];
    cmds.textField('InputCSVPath', edit=1, text=path2)

def ConvertCSV(myVal, _ignore):
    csvFilePath = cmds.textField('InputCSVPath', q=True, text=True)
    ApplyCSV(csvFilePath)    
        
def ApplyCSV(data_path) :  
    if not data_path:
        return
    data = {}
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    exceptLst = [
        'Timecode', 
        'BlendShapeCount',
        'HeadYaw',
        'HeadPitch',
        'HeadRoll',
        'LeftEyeYaw',  
        'LeftEyePitch',
        'LeftEyeRoll',
        'RightEyeYaw',  
        'RightEyePitch',
        'RightEyeRoll',
    ]
    with open(data_path,'r') as f:
        reader = csv.DictReader(f)
        x=0   
        
        for line in reader:
            data[x]={k:round(float(v),2) for k,v in line.items() if not 'Timecode' in k and v and not k in exceptLst}
            x+=1
    ns = cmds.optionMenu('nameSpaceMenu',v=True,q=True)
    blendShapeNode = cmds.textFieldButtonGrp('blNodeField',q=True,tx=True)
    if not blendShapeNode:
        blendShapeNode = 'asARKit'
    if ns:
        blendShapeNode = '%s:%s' % (ns,blendShapeNode)  
              
    cmds.progressBar( gMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=True,
                    status='Transfer blendshape Keys',
                    maxValue=len(data.items()))
    for key,attrData in data.items():
        
        for attr,value in attrData.items():
            cmds.setKeyframe(blendShapeNode,at = attr,t=key,v=float(value))
        
        cmds.progressBar(gMainProgressBar,e=True,step=1)
    cmds.progressBar(gMainProgressBar,e=True,ep=True)
    
def helpFunc(*args):
    fileName = os.path.join(manualPath, 'CSVToBlendShape.jpg')
    if cmds.window('CSVConvertHelp',ex=True):
        cmds.deleteUI('CSVConvertHelp')
    cmds.window('CSVConvertHelp',s=False,cc=lambda:print(cmds.window('CSVConvertHelp',wh=True,q=True)))
    cmds.paneLayout('CSVConvertHelpBGC')
    cmds.image(i=fileName)
    cmds.showWindow()
    cmds.window('CSVConvertHelp',e=True,wh=(866,292))  
        
def main():
    if cmds.window('dataConverter',ex=True):
        cmds.deleteUI('dataConverter')
    nsLst = [i for i in cmds.namespaceInfo(lon=True) if not 'UI' in i and not 'shared' in i]
    # Create a window
    window = cmds.window('dataConverter', menuBar=True,title="CSV Convert Control", iconName='CSVControlLoader', widthHeight=(320, 230), sizeable = True )
    cmds.menu(l='Manual',pmc=helpFunc)
    cmds.columnLayout(w=320, rs=10)
    cmds.rowLayout(w=320,nc=2)
    cmds.optionMenu('nameSpaceMenu',l='nameSpace:')
    for ns in nsLst:
        cmds.menuItem(ns,l=ns)
    #cmds.separator( height=10, style='none' )
    cmds.iconTextButton(style='iconOnly',image1=os.path.join(iconPath,'refresh.png'),c=refreshNS)
    cmds.setParent('..')

    # Find path
    cmds.rowColumnLayout('rlRun', nc=2, cw=[(1,100),(2,215)])
    cmds.text( label=' File Path : ', align='left' )                      
    front = cmds.textField('InputCSVPath', tx="Input Path")
            
    cmds.columnLayout(w=320, rs=20)
    cmds.button(label='Find Path  *.CSV', w=320, command = partial(OpenDir, "Click"))
    cmds.textFieldButtonGrp('blNodeField',l='Node name:',bl='<<',cl3=('left','left','left'),cw3=(80,180,30),bc=lambda:cmds.textFieldButtonGrp('blNodeField',e=True,tx=cmds.ls(sl=True)[0]))
    # Apply
    cmds.rowColumnLayout('rlRun', nc=2, cw=[(1,100),(2,215)])
    cmds.text( label=' Start Frame : ', align='left' )                      
    startFrm = cmds.intField('startFrm', value=0)

    cmds.columnLayout(w=320, rs=20)
    cmds.button(label='Apply Control', w=320, command = partial(ConvertCSV, "Click"))
            
    # delete
    cmds.rowColumnLayout('rlRun', nc=2, cw=[(1,100),(2,215)])
    cmds.text( label=' Delete start key : ', align='left' )                      
    startdel = cmds.intField('StartDel', value=1)

    cmds.text( label=' Delete end key : ', align='left' )                  
    enddel = cmds.intField('EndDel', value=1000)

    cmds.columnLayout(w=320, rs=10)
    cmds.button(label='Delete all keys', w=320, command = partial(DeleteKey, "Click"))

    # Set its parent to the Maya window (denoted by '..')
    cmds.setParent( '..' )
    
    # Show window
    cmds.showWindow( window ) 