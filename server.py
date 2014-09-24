import web

web.config.debug = False

urls = (
            "/games/thisgame", "ThisGame",
        )

app = web.application(urls, globals())
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer= {'count':0}




if __name__ == "__main__":
    app.run()
