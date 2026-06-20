import React from 'react'

const ApplicationTracker = ({ currentStage }) => {
  const stages = [
    {
      id: 0,
      title: 'Application Submission',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    },
    {
      id: 1,
      title: 'Documentation Review',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      )
    },
    {
      id: 2,
      title: 'Underwriting',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      )
    },
    {
      id: 3,
      title: 'Status',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
  ]

  const getStageState = (stageId) => {
    if (stageId < currentStage) return 'Done'
    if (stageId === currentStage) return 'Progress'
    return 'Pending'
  }

  const getStageColors = (state) => {
    switch (state) {
      case 'Done':
        return {
          bg: 'bg-green-500',
          text: 'text-green-700',
          badgeBg: 'bg-green-100',
          ring: 'ring-green-200'
        }
      case 'Progress':
        return {
          bg: 'bg-primary-500',
          text: 'text-primary-700',
          badgeBg: 'bg-primary-100',
          ring: 'ring-primary-200'
        }
      case 'Pending':
        return {
          bg: 'bg-navy-300',
          text: 'text-navy-600',
          badgeBg: 'bg-navy-100',
          ring: 'ring-navy-200'
        }
      default:
        return {
          bg: 'bg-navy-300',
          text: 'text-navy-600',
          badgeBg: 'bg-navy-100',
          ring: 'ring-navy-200'
        }
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-navy-900 tracking-tight">Application Tracker</h2>
      </div>

      {/* Horizontal Stepper */}
      <div className="relative">
        {/* Connection Lines */}
        <div className="absolute top-8 left-0 right-0 h-1 bg-navy-200 hidden sm:block" style={{ marginLeft: '2rem', marginRight: '2rem' }} />

        {/* Progress Line */}
        <div
          className="absolute top-8 left-0 h-1 bg-primary-500 hidden sm:block transition-all duration-500"
          style={{
            marginLeft: '2rem',
            width: `calc(${(currentStage / (stages.length - 1)) * 100}% - 2rem)`
          }}
        />

        {/* Stages */}
        <div className="relative grid grid-cols-2 sm:grid-cols-4 gap-4">
          {stages.map((stage, index) => {
            const state = getStageState(stage.id)
            const colors = getStageColors(state)

            return (
              <div key={stage.id} className="flex flex-col items-center">
                {/* Icon Circle */}
                <div className={`relative z-10 w-16 h-16 rounded-full ${colors.bg} flex items-center justify-center text-white shadow-lg ring-4 ${colors.ring} transition-all duration-300`}>
                  {state === 'Done' ? (
                    <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : state === 'Progress' ? (
                    <div className="relative">
                      {stage.icon}
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full animate-ping" />
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full" />
                    </div>
                  ) : (
                    stage.icon
                  )}
                </div>

                {/* Stage Title */}
                <h3 className={`mt-4 text-sm font-bold text-center ${colors.text} px-2`}>
                  {stage.title}
                </h3>

                {/* Status Badge */}
                <span className={`mt-2 px-3 py-1 rounded-full text-xs font-bold ${colors.badgeBg} ${colors.text}`}>
                  {state}
                </span>

                {/* Additional Info for Current Stage */}
                {state === 'Progress' && (
                  <p className="mt-2 text-xs text-navy-600 text-center px-2">
                    In progress...
                  </p>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Progress Summary */}
      <div className="mt-8 pt-6 border-t border-navy-200">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-navy-700">Overall Progress</span>
          <span className="text-sm font-bold text-navy-900">{Math.round((currentStage / (stages.length - 1)) * 100)}%</span>
        </div>
        <div className="w-full bg-navy-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-full rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${(currentStage / (stages.length - 1)) * 100}%` }}
          />
        </div>
        <p className="text-xs text-navy-600 mt-3 text-center">
          {currentStage === stages.length - 1
            ? 'Your application is complete!'
            : `Currently at stage ${currentStage + 1} of ${stages.length}`}
        </p>
      </div>
    </div>
  )
}

export default ApplicationTracker
