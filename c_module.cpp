#include <vector>
#include <limits>

extern "C" {
	#include <Python.h>
}

namespace c_module
{
	typedef std::vector<double> row_t;
	typedef std::vector<row_t> matrix_t;

	static matrix_t res_calc(const matrix_t& M) {
		
		matrix_t final_matrix = M;
		size_t size = M.size();
		unsigned int k, i, j;
		for (k = 0; k < size; k++) {
			for (i = 0; i < size; i++) {
				for (j = 0; j < size; j++) {
					if (final_matrix[i][j] == 0 || final_matrix[i][k] + final_matrix[k][j] == 0) {
						final_matrix[i][j] = 0;
					}
					else if (1/final_matrix[i][j] + 1/(final_matrix[i][k] + final_matrix[k][j]) == 0) {
						final_matrix[i][j] = std::numeric_limits<double>::infinity();
					}
					else {
						final_matrix[i][j] = 1/(1/final_matrix[i][j] + 1/(final_matrix[i][k] + final_matrix[k][j]));
					}
				}
			}
		}
		return final_matrix;
	}
}


static c_module::matrix_t pyobject_to_cxx(PyObject * py_matrix)
{
	c_module::matrix_t result;
	result.resize(PyObject_Length(py_matrix));
	for (size_t i=0; i<result.size(); ++i) {
		PyObject * py_row = PyList_GetItem(py_matrix, i);
		c_module::row_t & row = result[i];
		row.resize(PyObject_Length(py_row));
		for (size_t j=0; j<row.size(); ++j) {
			PyObject * py_elem = PyList_GetItem(py_row, j);
			const double elem = PyFloat_AsDouble(py_elem);
			row[j] = elem;
		}
	}
	return result;
}

static PyObject * cxx_to_pyobject(const c_module::matrix_t &matrix)
{
	PyObject * result = PyList_New(matrix.size());
	for (size_t i=0; i<matrix.size(); ++i) {
		const c_module::row_t & row = matrix[i];
		PyObject * py_row = PyList_New(row.size());
		PyList_SetItem(result, i, py_row);
		for (size_t j=0; j<row.size(); ++j) {
			const double elem = row[j];
			PyObject * py_elem = PyFloat_FromDouble(elem);
			PyList_SetItem(py_row, j, py_elem);
		}
	}
	return result;
}

static PyObject * matrixops_faster_res_calc(PyObject * module, PyObject * args)
{
	PyObject * py_a = PyTuple_GetItem(args, 0);

	/* Convert to C++ structure */
	const c_module::matrix_t a = pyobject_to_cxx(py_a);

	/* Perform calculations */
	const c_module::matrix_t result = c_module::res_calc(a);

	/* Convert back to Python object */
	PyObject * py_result = cxx_to_pyobject(result);
	return py_result;
}

PyMODINIT_FUNC PyInit_c_module()
{
	static PyMethodDef ModuleMethods[] = {
		{ "faster_res_calc", matrixops_faster_res_calc, METH_VARARGS, "Fater matrix production" },
		{ NULL, NULL, 0, NULL }
	};
	static PyModuleDef ModuleDef = {
		PyModuleDef_HEAD_INIT,
		"c_module",
		"Matrix operations",
		-1, ModuleMethods, 
		NULL, NULL, NULL, NULL
	};
	PyObject * module = PyModule_Create(&ModuleDef);
	return module;
}