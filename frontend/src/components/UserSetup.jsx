import React, { useState, useEffect } from 'react'
import {
  getAdminTables,
  getTableSchema,
  getTableRows,
  createTableRow,
  deleteTableRow
} from '../api/client'

const UserSetup = () => {
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState('')
  const [schema, setSchema] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({})

  // Load tables on mount
  useEffect(() => {
    const loadTables = async () => {
      try {
        const data = await getAdminTables()
        setTables(data.tables || [])
      } catch (err) {
        setError('Failed to load tables: ' + (err.response?.data?.detail || err.message))
      }
    }
    loadTables()
  }, [])

  // Load schema and rows when table is selected
  useEffect(() => {
    if (!selectedTable) {
      setSchema([])
      setRows([])
      return
    }

    const loadTableData = async () => {
      setLoading(true)
      setError('')
      try {
        const [schemaData, rowsData] = await Promise.all([
          getTableSchema(selectedTable),
          getTableRows(selectedTable)
        ])
        setSchema(schemaData.columns || [])
        setRows(rowsData.rows || [])

        // Initialize form data with empty values
        const initialFormData = {}
        schemaData.columns?.forEach(col => {
          // Skip auto-increment fields
          if (!isAutoIncrementField(col)) {
            initialFormData[col.name] = ''
          }
        })
        setFormData(initialFormData)
      } catch (err) {
        setError('Failed to load table data: ' + (err.response?.data?.detail || err.message))
      } finally {
        setLoading(false)
      }
    }

    loadTableData()
  }, [selectedTable])

  const isAutoIncrementField = (column) => {
    // Check if field is auto-increment (typically primary key integers)
    return column.pk === 1 && column.type === 'INTEGER'
  }

  const handleTableChange = (e) => {
    setSelectedTable(e.target.value)
    setShowAddForm(false)
    setError('')
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddRow = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Convert form data to appropriate types based on schema
      const typedData = {}
      schema.forEach(col => {
        if (formData.hasOwnProperty(col.name)) {
          const value = formData[col.name]
          if (value === '' && !col.notnull) {
            // Skip optional empty fields
            return
          }
          if (col.type === 'INTEGER') {
            typedData[col.name] = parseInt(value, 10)
          } else {
            typedData[col.name] = value
          }
        }
      })

      await createTableRow(selectedTable, typedData)

      // Reload rows
      const rowsData = await getTableRows(selectedTable)
      setRows(rowsData.rows || [])

      // Clear form
      const clearedFormData = {}
      schema.forEach(col => {
        if (!isAutoIncrementField(col)) {
          clearedFormData[col.name] = ''
        }
      })
      setFormData(clearedFormData)
      setShowAddForm(false)
    } catch (err) {
      setError('Failed to add row: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteRow = async (row) => {
    if (!window.confirm('Are you sure you want to delete this row?')) {
      return
    }

    setLoading(true)
    setError('')

    try {
      // Find primary key column(s)
      const pkColumns = schema.filter(col => col.pk)
      const primaryKey = {}
      pkColumns.forEach(col => {
        primaryKey[col.name] = row[col.name]
      })

      await deleteTableRow(selectedTable, primaryKey)

      // Reload rows
      const rowsData = await getTableRows(selectedTable)
      setRows(rowsData.rows || [])
    } catch (err) {
      setError('Failed to delete row: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const getInputType = (columnType) => {
    if (columnType === 'INTEGER') return 'number'
    return 'text'
  }

  return (
    <div className="bg-white rounded-lg p-6 card-clean border border-navy-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-navy-900">Table Editor</h2>
          <p className="text-sm text-navy-600">Manage database tables</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Table Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-navy-700 mb-2">
          Select Table
        </label>
        <select
          value={selectedTable}
          onChange={handleTableChange}
          className="w-full px-4 py-2 border border-navy-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">-- Choose a table --</option>
          {tables.map(table => (
            <option key={table} value={table}>{table}</option>
          ))}
        </select>
      </div>

      {/* Empty State */}
      {!selectedTable && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-navy-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <p className="text-navy-600">Select a table to view and edit its data</p>
        </div>
      )}

      {/* Table Content */}
      {selectedTable && (
        <>
          {/* Add Row Button */}
          <div className="mb-4 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-navy-800">
              {selectedTable} ({rows.length} rows)
            </h3>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
              disabled={loading}
            >
              {showAddForm ? 'Cancel' : 'Add Row'}
            </button>
          </div>

          {/* Add Row Form */}
          {showAddForm && (
            <div className="mb-6 p-4 bg-gray-50 border border-navy-200 rounded-lg">
              <h4 className="text-md font-semibold text-navy-800 mb-4">Add New Row</h4>
              <form onSubmit={handleAddRow}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {schema.filter(col => !isAutoIncrementField(col)).map(col => (
                    <div key={col.name}>
                      <label className="block text-sm font-medium text-navy-700 mb-1">
                        {col.name}
                        {col.notnull && <span className="text-red-500 ml-1">*</span>}
                        <span className="text-xs text-navy-500 ml-2">({col.type})</span>
                      </label>
                      <input
                        type={getInputType(col.type)}
                        name={col.name}
                        value={formData[col.name] || ''}
                        onChange={handleFormChange}
                        required={col.notnull}
                        className="w-full px-3 py-2 border border-navy-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                      />
                    </div>
                  ))}
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:bg-gray-400"
                >
                  {loading ? 'Adding...' : 'Submit'}
                </button>
              </form>
            </div>
          )}

          {/* Loading State */}
          {loading && !showAddForm && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <p className="mt-2 text-navy-600">Loading...</p>
            </div>
          )}

          {/* Data Table */}
          {!loading && schema.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-navy-200">
                <thead className="bg-navy-50">
                  <tr>
                    {schema.map(col => (
                      <th
                        key={col.name}
                        className="px-4 py-3 text-left text-xs font-semibold text-navy-700 uppercase tracking-wider"
                      >
                        {col.name}
                        {col.pk === 1 && <span className="ml-1 text-primary-600">🔑</span>}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-left text-xs font-semibold text-navy-700 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-navy-100">
                  {rows.length === 0 ? (
                    <tr>
                      <td colSpan={schema.length + 1} className="px-4 py-8 text-center text-navy-500">
                        No rows found
                      </td>
                    </tr>
                  ) : (
                    rows.map((row, idx) => (
                      <tr key={idx} className="hover:bg-navy-50 transition-colors">
                        {schema.map(col => (
                          <td key={col.name} className="px-4 py-3 text-sm text-navy-900">
                            {row[col.name] !== null ? String(row[col.name]) : <span className="text-navy-400 italic">null</span>}
                          </td>
                        ))}
                        <td className="px-4 py-3 text-sm">
                          <button
                            onClick={() => handleDeleteRow(row)}
                            disabled={loading}
                            className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-xs font-medium disabled:bg-gray-400"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default UserSetup
