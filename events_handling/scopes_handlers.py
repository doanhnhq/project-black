from netaddr import IPNetwork
from flask_socketio import emit


class ScopeHandlers(object):
    def __init__(self, socketio, scope_manager):
        @socketio.on('scopes:all:get')
        def handle_custom_event():
            """ When received this message, send back all the scopes """
            socketio.emit('scopes:all:get:back', {
                'status' : 'success',
                'ips' : scope_manager.get_scopes(),
                'hosts': scope_manager.get_hosts()
            }, broadcast=True)


        @socketio.on('scopes:create')
        def handle_scope_creation(msg):
            """ When received this message, create a new scope """
            scopes = msg['scopes']
            project_uuid = msg['project_uuid']

            new_scopes = []

            error_found = False
            error_text = ""

            for scope in scopes:
                added = False
                # Create new scope (and register it)
                if scope['type'] == 'hostname':
                    create_result = scope_manager.create_scope(None, scope['target'], project_uuid)
                elif scope['type'] == 'ip_address':
                    create_result = scope_manager.create_scope(scope['target'], None, project_uuid)
                elif scope['type'] == 'network':
                    ips = IPNetwork(scope['target'])

                    for ip_address in ips:
                        create_result = scope_manager.create_scope(None, str(ip_address), project_uuid)

                        if create_result["status"] == "success":
                            new_scope = create_result["new_scope"]

                            if new_scope:
                                added = True
                                new_scopes.append(new_scope)
                else:
                    create_result = {
                        "status": 'error',
                        "text": "Something bad was sent upon creating scope"
                    }

                if not added and create_result["status"] == "success":
                    new_scope = create_result["new_scope"]

                    if new_scope:
                        new_scopes.append(new_scope)
                    
                elif create_result["status"] == "error":
                    error_found = True
                    new_err = create_result["text"]

                    if new_err not in error_text:
                        error_text += new_err

            if error_found:     
                socketio.emit('scopes:create', {
                    'status': 'error',
                    'project_uuid': project_uuid,
                    'text': error_text
                }, broadcast=True)

            else:
                # Send the scope back
                socketio.emit('scopes:create', {
                    'status': 'success',
                    'project_uuid': project_uuid,
                    'new_scopes': new_scopes
                }, broadcast=True)


        @socketio.on('scopes:delete:scope_id')
        def handle_scope_deletiong(msg):
            """ When received this message, delete the scope """
            scope_id = msg['scope_id']

            # Delete new scope (and register it)
            delete_result = scope_manager.delete_scope(scope_id=scope_id)

            if delete_result["status"] == "success":
                # Send the success result
                socketio.emit('scopes:delete', {
                    'status': 'success',
                    '_id': scope_id
                }, broadcast=True)

            else:
                # Error occured
                socketio.emit('scopes:delete', {
                    'status': 'error',
                    'text': delete_result["text"]
                }, broadcast=True)

        @socketio.on('scopes:resolve')
        def handle_scopes_resolver(msg):
            """ On receive, resolve the needed scope """
            scopes_ids = msg['scopes_ids']
            project_uuid = msg['project_uuid']

            scope_manager.resolve_scopes(project_uuid, scopes_ids)
            socketio.emit('scopes:all:get:back', {
                'status' : 'success',
                'scopes' :scope_manager.get_scopes()
            }, broadcast=True)

        @socketio.on('scopes:update')
        def handle_scope_update(msg): 
            """ Update the scope (now only used for comment). """
            scope_id = msg['scope_id']
            comment = msg['comment']

            result = scope_manager.update_scope(scope_id=scope_id, comment=comment)
            if result["status"] == "success":
                updated_scopes = result["updated_scopes"]

                socketio.emit('scopes:update:back', {
                    "status": "success",
                    "updated_scopes": updated_scopes
                })
            else :
                socketio.emit('scopes:update:back', result)
