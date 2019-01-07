import numpy as np


def write_project_hdf(data, filename):
    """Writes the project data dictionary to a hdf file

    :param data: A dictionary containing the project data
    :type data: dict
    :param filename: path of the hdf file
    :type filename: str
    """
    import h5py
    import datetime as dt
    from sscanss.version import __version__

    with h5py.File(filename, 'w') as hdf_file:
        hdf_file.attrs['name'] = data['name']
        hdf_file.attrs['version'] = __version__

        date_created = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hdf_file.attrs['date_created'] = date_created


def write_binary_stl(filename, mesh):
    """Writes a 3D mesh to a binary STL file. The binary STL format only
    supports face normals while the Mesh object stores vertex normals
    therefore the first vertex normal for each face is written.

    :param filename: path of the stl file
    :type filename: str
    :param mesh: The vertices, normals and index array of the mesh
    :type mesh: sscanss.core.mesh.Mesh
    """
    record_dtype = np.dtype([
        ('normals', np.float32, (3,)),
        ('vertices', np.float32, (3, 3)),
        ('attr', '<i2', (1,)),
    ])
    face_count = mesh.indices.size // 3
    data = np.recarray(face_count, dtype=record_dtype)

    data.normals = mesh.normals[mesh.indices, :][::3]
    data.attr = np.zeros((face_count, 1), dtype=np.uint32)
    data.vertices = mesh.vertices[mesh.indices, :].reshape((-1, 3, 3))

    with open(filename, 'wb') as stl_file:
        stl_file.seek(80)
        np.array(face_count, dtype=np.int32).tofile(stl_file)
        data.tofile(stl_file)
