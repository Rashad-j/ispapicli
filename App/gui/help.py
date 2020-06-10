from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings


class Render(QWebEngineView):
    def __init__(self, html):
        self.html = None
        self.app = QApplication(sys.argv)
        QWebEngineView.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.setHtml(html)
        self.app.exec_()

    def _loadFinished(self, result):
        # what's going on here? how can I get the HTML from toHtml?
        self.page().toHtml(self.callable)
        self.app.quit()

    def callable(self, data):
        self.html = data