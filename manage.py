import flask_script
import flask_migrate

import web
import web.commands.pubsub


app = web.create_app()
migrate = flask_migrate.Migrate(app, app.db)

manager = flask_script.Manager(app)
manager.add_command('db', flask_migrate.MigrateCommand)
manager.add_command('pubsub', web.commands.pubsub.PubSubCommand)


if __name__ == '__main__':
    manager.run()
