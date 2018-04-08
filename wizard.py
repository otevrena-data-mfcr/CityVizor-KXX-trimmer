import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QWizard, QWizardPage, QProgressBar, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QProgressBar
from PyQt5.QtGui import QIcon


class MagicWizard(QWizard):
    def __init__(self, parent=None):
        super(MagicWizard, self).__init__(parent)
        self.addPage(LoadPage(self))
        self.addPage(TransformPage(self))
        self.setWindowTitle("KXX Remover")
        self.resize(640,480)

 
class LoadPage(QWizardPage):
    def __init__(self, parent=None):
        super(LoadPage, self).__init__(parent)

        btnLoadSource = QPushButton('Načíst zdrojový soubor KXX', self)
        btnLoadSource.clicked.connect(self.openFileNameDialog)
        
        self.textbox = QLineEdit(self)

        layout = QVBoxLayout()
        layout.addWidget(btnLoadSource)
        layout.addWidget(self.textbox)

        self.registerField("sourcePath*", self.textbox)

        self.setLayout(layout)

    def getSourcePath(self):
        return self.textbox.text()

    def openFileNameDialog(self):    
        options = QFileDialog.Options()
        fileName = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","KXX Files (*.kxx)", options=options)
        if fileName:
            self.textbox.setText(fileName[0])            

class TransformPage(QWizardPage):
    def __init__(self, parent=None):
        super(TransformPage, self).__init__(parent)
        
        self.progress = QProgressBar(self)

        layout = QVBoxLayout()
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def initializePage(self):
        self.transform()

    def file_len(self,fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def transform(self):

        sourcePath = self.field("sourcePath")
        sourceName = os.path.splitext(sourcePath)[0]
        
        sourceLines = self.file_len(sourcePath)
        
        targetPath = sourceName + "_upraveno.kxx"
        logPath = sourceName + "_zmeny.csv"

        with open(sourcePath,"r",encoding="windows-1250") as sourceFile:
            with open(targetPath,"w",encoding="windows-1250") as targetFile:
                with open(logPath,"w",encoding="windows-1250") as logFile:

                    logFile.write("\"Typ záznamu\";\"Číslo záznamu\";\"Změna\";\"\"\n")                    

                    for lineNum, line in enumerate(sourceFile):

                        line = line.strip()
                        
                        p = re.compile('^(G\/\#000\d)(\d+).*\\\\n')
                        match = p.match(line)

                        if match:

                            parts = line.split("\\n")                

                            targetFile.write(parts[0])
                            logFile.write("\"" + match.group(1) + "\";\"" + match.group(2) + "\";\"Původní:\";\"" + line.replace("\"","\"\"") + "\"\n")
                            logFile.write(";;\"Nové:\";\"" + parts[0].replace("\"","\"\"") + "\"\n\n")
                        
                        else:
                            targetFile.write(line)

                        self.progress.setValue((lineNum + 1) / sourceLines * 100)
 
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wizard = MagicWizard()
    wizard.show()
    sys.exit(app.exec_())