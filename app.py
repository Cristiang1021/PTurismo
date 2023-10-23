from flask import Flask
from flask import render_template,request,redirect,url_for, flash,Response, session
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
from pymysql.cursors import DictCursor
import os


app= Flask(__name__)
app.secret_key="Proyecto"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '' 
app.config['MYSQL_DATABASE_DB'] = 'turism'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/sesion')
def iniciar():
    return render_template('sesion.html')

#MOSTRAR DATOS
@app.route('/usuarios')
def index():
    sql = "SELECT * FROM `usuarios`;"
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    usuarios=cursor.fetchall()
    print(usuarios)
    conn.commit()
    return render_template('usuarios/index.html',usuarios=usuarios)

#ELIMINAR
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor=conn.cursor()
    
    cursor.execute("SELECT foto_perfil FROM usuarios WHERE id=%s",id)
    fila=cursor.fetchall()
        
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    
    cursor.execute("DELETE FROM usuarios WHERE id=%s",(id))
    conn.commit()
    return redirect('/')

#EDITAR
@app.route('/edit/<int:id>')
def edit(id):
    
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id))
    usuarios=cursor.fetchall()
    conn.commit()
    return render_template('usuarios/edit.html',usuarios=usuarios)

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _apellido=request.form['txtApellido']
    _correo=request.form['txtCorreo']
    _contrasena=request.form['txtContrasena']
    _foto=request.files['txtFoto']
    _telefono=request.form['txtTelefono']
    id=request.form['txtID']
    
    sql = "UPDATE usuarios SET `nombre`=%s, `apellido`=%s, `email`=%s, `contraseña`=%s, `telefono`=%s WHERE id=%s;"
    datos=(_nombre,_apellido,_correo,_contrasena,_telefono,id)
    conn = mysql.connect()
    cursor=conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename!='':

        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto_perfil FROM usuarios WHERE id=%s",id)
        fila=cursor.fetchall()
        
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE usuarios SET foto_perfil=%s WHERE id=%s",(nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    
    
    return redirect('/')

@app.route('/registrarse')
def registrarse():
    return render_template('usuarios/registrarse.html')


#MANDAR DATOS DE UN FORMULARIO A OTRO
@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _apellido=request.form['txtApellido']
    _correo=request.form['txtCorreo']
    _contrasena=request.form['txtContrasena']
    _foto=request.files['txtFoto']
    _telefono=request.form['txtTelefono']

    if _nombre=='' or _correo=='' or _apellido=='' or _contrasena=='' or _foto=='' or _telefono=='':
        flash('Debes llenar todos los campos')
        return redirect(url_for('registrarse'))
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `usuarios` (`id`, `nombre`, `apellido`, `email`, `contraseña`, `foto_perfil`, `telefono`, `rol_id`) VALUES (NULL, %s, %s, %s, %s, %s, %s, '1');"
    datos=(_nombre,_apellido,_correo,_contrasena,nuevoNombreFoto,_telefono)
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')
    
@app.route('/admin')
def admin():
    return render_template('admin/index.html')


#LOGIN
@app.route('/login', methods=["GET","POST"])
def acceso():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtContrasena':
        _correo = request.form['txtCorreo']
        _contrasena = request.form['txtContrasena']
        
        sql = "SELECT * FROM usuarios WHERE email =%s AND contraseña =%s;"
        conn = mysql.connect()
        cursor = conn.cursor(DictCursor)
        cursor.execute(sql,(_correo, _contrasena))
        account = cursor.fetchone()
        

        
        if  _correo=='' or _contrasena=='' :
            flash('Debes llenar todos los campos')
            return redirect(url_for('iniciar'))

        if account:
            session['Logueado'] = True
            session['id'] = account['id']
            session['rol_id'] = account['rol_id']
            if session['rol_id'] == 2:
                flash('Administrador conectado satisfcatoriamente')
                return redirect(url_for('admin'))
            elif session['rol_id'] == 1:
                flash('Usuario conectado satisfcatoriamente')
                return redirect(url_for('inicio'))
        else:
            flash('Usuario incorrecto')
            return redirect('/sesion')

if __name__== '__main__':
    app.run(debug=True, port=3000)