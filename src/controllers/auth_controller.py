from flask import redirect, url_for, flash, render_template, request, session as flask_session, jsonify
from src.controllers.base_controller import FlaskController, route
from datetime import datetime, timezone
from src.models import session as db_session
from src.models.usuario import Usuario, RolUsuario
from src.password_utils import validar_contraseña
from src.models.empleado import Empleado
from flask_cors import cross_origin

class AuthController(FlaskController):
    MAX_INTENTOS_FALLIDOS = 3
    
    def __init__(self):
        super().__init__()
        # Cambiamos el prefijo para que coincida con las rutas del cliente
        # o dejamos sin prefijo para que sea relativo a la raíz
        self.url_prefix = '/'

    @route('auth', methods=['GET', 'POST'])
    def login(self):
        print("Método de solicitud:", request.method)  # Log inicial
        
        if request.method == 'POST':
            nombre_usuario = request.form.get('nombre_usuario')
            contraseña = request.form.get('contraseña')
            print(f"Intento de login para usuario: {nombre_usuario}")  # Log de intento
            
            try:
                user = db_session.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
                
                if not user:
                    print("Usuario no encontrado")  # Log de usuario no encontrado
                    flash('Usuario no encontrado', 'danger')
                    return render_template('login.html')
                
                if not user.habilitado:
                    print("Usuario deshabilitado")  # Log de usuario deshabilitado
                    flash(f'Su cuenta ha sido deshabilitada. Causa: {user.causa_suspension}', 'danger')
                    return render_template('login.html')
                
                if not user.check_password(contraseña):
                    print("Contraseña incorrecta")  # Log de contraseña incorrecta
                    user.intentos_fallidos += 1
                    
                    if user.intentos_fallidos >= self.MAX_INTENTOS_FALLIDOS:
                        user.suspender_usuario("Exceso de intentos fallidos de inicio de sesión")
                        flash('Su cuenta ha sido suspendida por seguridad', 'danger')
                    else:
                        intentos_restantes = self.MAX_INTENTOS_FALLIDOS - user.intentos_fallidos
                        flash(f'Contraseña incorrecta. Intentos restantes: {intentos_restantes}', 'danger')
                    
                    db_session.commit()
                    return render_template('login.html')
                
                # Si llegamos aquí, la autenticación fue exitosa
                print(f"Autenticación exitosa para {user.nombre_usuario}")  # Log de éxito
                
                user.intentos_fallidos = 0
                user.ultima_sesion = datetime.now(timezone.utc)
                
                # Establecer la sesión
                flask_session.clear()  # Limpiar cualquier sesión anterior
                flask_session.permanent = True
                flask_session['logged_in'] = True
                flask_session['user_id'] = user.id_usuario
                flask_session['user_role'] = user.rol.value
                flask_session['empleado_id'] = user.empleado.id_empleado
                flask_session['permisos'] = user.get_permissions()
                
                print("Valores establecidos en la sesión:", dict(flask_session))  # Log de sesión
                
                # Guardar cambios en la base de datos
                db_session.commit()
                
                flash('Inicio de sesión exitoso', 'success')
                print("Redirigiendo a dashboard...")  # Log de redirección
                
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                print(f"Error en login: {str(e)}")  # Log de error
                db_session.rollback()
                flash(f'Error al iniciar sesión: {str(e)}', 'danger')
                return render_template('login.html')
        
        return render_template('login.html')

    # Corregimos la ruta para que sea exactamente /api/login
    @route('api/login', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def api_login(self):
        try:
            print("Recibida solicitud en /api/login")  # Añadimos log para depurar
            data = request.get_json()
            print(f"Datos recibidos: {data}")  # Añadimos log para ver los datos
            
            if not data or 'username' not in data or 'password' not in data:
                print("Datos incompletos en la solicitud")
                return jsonify({
                    'success': False, 
                    'error': 'Datos incompletos'
                }), 400
                
            username = data['username']
            password = data['password']
            
            # Buscar usuario en la base de datos
            user = db_session.query(Usuario).filter_by(nombre_usuario=username).first()
            
            if not user:
                print(f"Usuario {username} no encontrado")
                return jsonify({
                    'success': False, 
                    'error': 'Usuario no encontrado'
                }), 401
                
            if not user.habilitado:
                return jsonify({
                    'success': False, 
                    'error': f'Su cuenta ha sido deshabilitada. Causa: {user.causa_suspension}'
                }), 401
                
            if not user.check_password(password):
                user.intentos_fallidos += 1
                
                if user.intentos_fallidos >= self.MAX_INTENTOS_FALLIDOS:
                    user.suspender_usuario("Exceso de intentos fallidos de inicio de sesión")
                    db_session.commit()
                    return jsonify({
                        'success': False, 
                        'error': 'Su cuenta ha sido suspendida por seguridad'
                    }), 401
                else:
                    intentos_restantes = self.MAX_INTENTOS_FALLIDOS - user.intentos_fallidos
                    db_session.commit()
                    return jsonify({
                        'success': False, 
                        'error': f'Contraseña incorrecta. Intentos restantes: {intentos_restantes}'
                    }), 401
                    
            # Si llegamos aquí, la autenticación fue exitosa
            print(f"API Login exitoso para {username}")
            user.intentos_fallidos = 0
            user.ultima_sesion = datetime.now(timezone.utc)
            
            # Establecer la sesión
            flask_session.clear()  # Limpiar cualquier sesión anterior
            flask_session.permanent = True
            flask_session['logged_in'] = True
            flask_session['user_id'] = user.id_usuario
            flask_session['user_role'] = user.rol.value
            if hasattr(user, 'empleado') and user.empleado:
                flask_session['empleado_id'] = user.empleado.id_empleado
            flask_session['permisos'] = user.get_permissions()
            
            print("Sesión establecida:", dict(flask_session))
            
            # Guardar cambios en la base de datos
            db_session.commit()
            
            return jsonify({
                'success': True,
                'user_id': user.id_usuario,
                'user_role': user.rol.value,
                'mensaje': 'Inicio de sesión exitoso'
            })
            
        except Exception as e:
            print(f"Error en API login: {str(e)}")
            db_session.rollback()
            return jsonify({
                'success': False,
                'error': f"Error interno: {str(e)}"
            }), 500
            
    # Corregimos las rutas para que sean exactamente las esperadas por el cliente
    @route('api/auth/status', methods=['GET'])
    @cross_origin(supports_credentials=True)
    def auth_status(self):
        # Verificar el estado de autenticación actual
        is_logged_in = flask_session.get('logged_in', False)
        user_role = flask_session.get('user_role', None) if is_logged_in else None
        user_id = flask_session.get('user_id', None) if is_logged_in else None
        empleado_id = flask_session.get('empleado_id', None) if is_logged_in else None
        permisos = flask_session.get('permisos', []) if is_logged_in else []
        
        print(f"Solicitud de estado de autenticación: {is_logged_in}")
        
        return jsonify({
            'logged_in': is_logged_in,
            'user_role': user_role,
            'user_id': user_id,
            'empleado_id': empleado_id,
            'permisos': permisos
        })
    
    @route('auth/forgot_password', methods=['GET', 'POST'])
    def forgot_password(self):
        """
        Maneja el proceso de recuperación de contraseña usando el correo electrónico
        en lugar del nombre de usuario
        """
        if request.method == 'POST':
            try:
                email = request.form.get('email')
                
                # Buscamos el empleado por email y luego obtenemos su usuario
                empleado = db_session.query(Empleado).filter_by(email=email).first()
                
                if empleado and empleado.usuario:
                    # Generamos una contraseña temporal segura
                    nueva_contraseña = self._generar_contraseña_temporal()
                    
                    # Actualizamos la contraseña del usuario
                    usuario = empleado.usuario
                    usuario.set_password(nueva_contraseña)
                    usuario.primer_ingreso = True  # Forzará cambio de contraseña en próximo ingreso
                    
                    # Enviamos el correo con la contraseña temporal
                    self._enviar_email_recuperacion(email, nueva_contraseña)
                    
                    db_session.commit()
                    flash('Se han enviado las instrucciones de recuperación a tu correo', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('No se encontró ninguna cuenta asociada a este correo', 'danger')
                    
            except Exception as e:
                db_session.rollback()
                flash(f'Error en la recuperación de contraseña: {str(e)}', 'danger')
        
        return render_template('forgot_password.html')

    def _generar_contraseña_temporal(self):
        """
        Genera una contraseña temporal segura combinando letras, números y símbolos
        """
        import secrets
        import string
        
        # Aseguramos que la contraseña tenga al menos un carácter de cada tipo
        letras_minusculas = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(3))
        letras_mayusculas = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        numeros = ''.join(secrets.choice(string.digits) for _ in range(3))
        simbolos = ''.join(secrets.choice('!@#$%&*') for _ in range(3))
        
        # Combinamos y mezclamos todos los caracteres
        contraseña = list(letras_minusculas + letras_mayusculas + numeros + simbolos)
        secrets.SystemRandom().shuffle(contraseña)
        
        return ''.join(contraseña)

    def _enviar_email_recuperacion(self, email, contraseña):
        """
        Envía el correo con la contraseña temporal y las instrucciones
        """
        try:
            mensaje = Message(
                'Recuperación de Contraseña - PerfumEasy',
                recipients=[email]
            )
            
            mensaje.body = f'''
           Has solicitado recuperar tu contraseña en PerfumEasy.
            
            Tu contraseña temporal es: {contraseña}
            
            Por favor, sigue estos pasos:
            1. Ingresa a la aplicación con esta contraseña temporal
            2. El sistema te pedirá cambiar tu contraseña inmediatamente
            3. Elige una nueva contraseña segura que puedas recordar
            
            Por seguridad, esta contraseña temporal expirará en 24 horas.
            
            Si no solicitaste este cambio, por favor contacta al administrador 
            del sistema inmediatamente.
            
            Saludos,
            Equipo PerfumEasy'''
            
            mail.send(mensaje)
            
        except Exception as e:
            flash(f'Error al enviar el correo de recuperación: {str(e)}', 'danger')
            raise  # Re-lanzamos la excepción para manejarla en forgot_password

    @route('auth/actualizar_credenciales', methods=['GET', 'POST'])
    def actualizar_credenciales(self):
        if not flask_session.get('logged_in'):
            return redirect(url_for('auth.login'))
            
        if request.method == 'POST':
            try:
                user = db_session.query(Usuario).get(flask_session['user_id'])
                nueva_contraseña = request.form.get('nueva_contraseña')
                confirmar_contraseña = request.form.get('confirmar_contraseña')
                
                if nueva_contraseña != confirmar_contraseña:
                    flash('Las contraseñas no coinciden', 'danger')
                    return render_template('actualizar_credenciales.html')
                
                if not validar_contraseña(nueva_contraseña):
                    flash('La contraseña no cumple con los requisitos de seguridad', 'danger')
                    return render_template('actualizar_credenciales.html')
                
                user.set_password(nueva_contraseña)
                user.primer_ingreso = False
                db_session.commit()
                
                flash('Contraseña actualizada exitosamente', 'success')
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                db_session.rollback()
                flash(f'Error al actualizar contraseña: {str(e)}', 'danger')
                return render_template('actualizar_credenciales.html')
        
        return render_template('actualizar_credenciales.html')

    @route('auth/logout', methods=['GET'])
    def logout(self):
        flask_session.clear()
        flash('Sesión cerrada exitosamente', 'success')
        return redirect(url_for('home.index'))
        
    # Corregimos la ruta para el logout de la API
    @route('api/logout', methods=['GET'])
    @cross_origin(supports_credentials=True)
    def api_logout(self):
        flask_session.clear()
        return jsonify({
            'success': True,
            'mensaje': 'Sesión cerrada correctamente'
        })