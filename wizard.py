import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QWizard, QLabel,QWizardPage, QProgressBar, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QProgressBar
from PyQt5.QtGui import QIcon


class TrimmerWizard(QWizard):
    def __init__(self, parent=None):
        super(TrimmerWizard, self).__init__(parent)
        self.addPage(InfoPage(self))
        self.addPage(LoadPage(self))
        self.addPage(TransformPage(self))
        self.setWindowTitle("CityVizor KXX Remover v0.1")
        self.resize(640,480)
 
class InfoPage(QWizardPage):
     def __init__(self, parent=None):
        super(InfoPage, self).__init__(parent)

        infoText = QLabel(self)
        infoText.setWordWrap(True)
        infoText.setText("Tento skript projde soubor *.KXX exportu z účetnictví firmy Gordic a vytvoří nový soubor, kde bude u všech textovích polí zachován pouze první řádek textu.\n\nToto je vývojová verze a je proto bez záruky.\n\nPro pokračování stiskněte tlačítko Další.")

        layout = QVBoxLayout()
        layout.addWidget(infoText)

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
        fileName = QFileDialog.getOpenFileName(self,"Vyberte zdrojový KXX soubor", "","KXX Files (*.kxx)", options=options)
        if fileName:
            self.textbox.setText(fileName[0])

class TransformPage(QWizardPage):
    def __init__(self, parent=None):
        super(TransformPage, self).__init__(parent)

        self.started = False
        self.complete = False
        
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        
        self.status = QLabel(self)
        self.status.setText("Klikněte na tlačítko Start pro začátek konverze")

        btnStart = QPushButton('Start', self)
        btnStart.clicked.connect(self.transform)

        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(btnStart)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def isComplete(self):
        return self.complete

    def file_len(self,fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def transform(self):

        if self.started:
            return

        sourcePath = self.field("sourcePath")
        sourceName = os.path.splitext(sourcePath)[0]
        sourceLines = self.file_len(sourcePath)
        
        targetPath = sourceName + "_upraveno.kxx"
        logPath = sourceName + "_zmeny.csv"

        if not os.path.isfile(sourcePath):
            self.status.setText("Zdrojový soubor nenalezen.")
            return

        self.started = True

        try:
            with open(sourcePath,"r",encoding="windows-1250") as sourceFile:
                try:
                    with open(targetPath,"w",encoding="windows-1250") as targetFile:
                        try:
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
                                    self.status.setText("Řádek %s z %s" % (str(lineNum + 1), str(sourceLines)))

                            self.status.setText("Hotovo!\n\nVýsledek je uložen v souboru " + os.path.basename(targetPath) + "\nSeznam změn je uložen v souboru " + os.path.basename(logPath))

                            self.complete = True
                            self.completeChanged.emit()

                            return

                        except IOError as x:
                            self.status.setText("Nastala chyba při otevírání souboru se seznamem změn.\n - Je v adresáři povolen zápis?\n - Není soubor otevřen v jiné aplikaci?")
            
                except IOError as x:
                    self.status.setText("Nastala chyba při otevírání cílového souboru.\n - Je v adresáři povolen zápis?\n - Není soubor otevřen v jiné aplikaci?")
        
        except IOError as x:
            self.status.setText("Nastala chyba při otevírání zdrojového souboru.")
            
        self.started = False
 
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wizard = TrimmerWizard()
    wizard.show()
    sys.exit(app.exec_())