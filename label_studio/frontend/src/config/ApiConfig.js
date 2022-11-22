export const API_CONFIG = {
  gateway: `${window.APP_SETTINGS.hostname}/api`,
  // gateway: `http://124.71.161.146:8080/api`,
  endpoints: {
    // Users
    users: "/users",
    usersList:"GET:/users/all",
    me: "/current-user/whoami",

    // Organization
    memberships: "/organizations/:pk/memberships",
    inviteLink: "/invite",
    resetInviteLink: "POST:/invite/reset-token",
    orgList: "GET:/organizations",
    allOrg:"GET:/organizations/all",
    addOrg: "POST:/organizations",
    updateOrg: "PATCH:/organizations/:pk",
    deleteOrg: "DELETE:/organizations/:pk",
    orgDetail: "GET:/organizations/:pk",
    changeOrg: "PATCH:/organizations/change",

    //Regist
    signInvite: "POST:/sign/invite",
    updateInvite: "PATCH:/sign/invite/:pk",
    roleList:"GET:/sign/invite/select",

    // Project
    projects: "/projects",
    project: "/projects/:pk",
    updateProject: "PATCH:/projects/:pk",
    createProject: "POST:/projects",
    deleteProject: "DELETE:/projects/:pk",
    addProjectRole:"POST:/projects/:pk/user",

    // Project Collection
    collections: "/project-set",
    collection: "/project-set/:id",
    createCollections: "POST:/project-set",
    deleteCollections: "DELETE:/project-set/:id",
    updateCollections: "PATCH:/project-set/:id",

    //Model manager
    modelManager: "GET:/model-manager",
    importModel: "POST:/model-manager",
    editModel: "PATCH:/model-manager/:pk",
    exportModel: "GET:/model-manager/:pk/export",
    filtersModel: "GET:/model-manager/select",
    modelList: "GET:/model-manager/model",
    modelLabel:"GET:/model-manager/label",

    // Config and Import
    configTemplates: "/templates",
    validateConfig: "POST:/projects/:pk/validate",
    createSampleTask: "POST:/projects/:pk/sample-task",
    fileUploads: "/projects/:pk/file-uploads",
    deleteFileUploads: "DELETE:/projects/:pk/file-uploads",
    importFiles: "POST:/projects/:pk/import",
    reimportFiles: "POST:/projects/:pk/reimport",
    dataSummary: "/projects/:pk/summary",

    // DM
    deleteTabs: "DELETE:/dm/views/reset",

    // Storages
    listStorages: "/storages/:target?",
    storageTypes: "/storages/:target?/types",
    storageForms: "/storages/:target?/:type/form",
    createStorage: "POST:/storages/:target?/:type",
    deleteStorage: "DELETE:/storages/:target?/:type/:pk",
    updateStorage: "PATCH:/storages/:target?/:type/:pk",
    syncStorage: "POST:/storages/:target?/:type/:pk/sync",
    validateStorage: "POST:/storages/:target?/:type/validate",

    // ML
    mlBackends: "GET:/ml",
    mlBackend: "GET:/ml/:pk",
    addMLBackend: "POST:/ml",
    updateMLBackend: "PATCH:/ml/:pk",
    deleteMLBackend: "DELETE:/ml/:pk",
    trainMLBackend: "POST:/ml/:pk/train",
    predictWithML: "POST:/ml/:pk/predict",
    modelVersions: "/projects/:pk/model-versions",
    mlInteractive: "POST:/ml/:pk/interactive-annotating",
    mlPreLabelProgress: "GET:/dbml/query_task",
    mlPredictProcess: "POST:/dbml/predict",
    mlProjectLabels: "GET:/projects/:pk/label",

    // Prompt Learning
    mlPromptPredict: 'POST:/projects/prompt-learning/predict',
    mlPromptTemplateCreate: 'POST:/templates/prompt-learning',
    mlPromptTemplateDelete: 'DELETE:/templates/prompt-learning',
    mlPromptTemplateUpdate: 'PATCH:/templates/prompt-learning',
    mlPromptTemplateQuery: 'GET:/templates/prompt-learning/:project',

    // Clean
    clExecClean: "POST:/dbml/clean",
    clReplace: "PATCH:/dbml/replace",
    clList: "GET:/clean_tag",
    clQueryStatus: "GET:/dbml/clean/query_task",
    clLabelManually: "PATCH:/clean_tag/:id",
    cancelJob: "GET:/dbml/cancel_job",

    // Export
    export: "/projects/:pk/export",
    previousExports: "/projects/:pk/export/files",
    exportFormats: "/projects/:pk/export/formats",

    // Version
    version: "/version",

    // Webhook
    webhooks: "/webhooks",
    webhook: "/webhooks/:pk",
    updateWebhook: "PATCH:/webhooks/:pk",
    createWebhook: "POST:/webhooks",
    deleteWebhook: "DELETE:/webhooks/:pk",
    webhooksInfo: "/webhooks/info",

    //人在环路
    listTrain: "/model-train",
    delTrain: "DELETE:/model-train/:pk",
    modelTrain: "/model-train/model",
    selectOfTrain: "/model-train/select",
    assessment: "POST:/model-train/assessment",
    train:"POST:/model-train/train",
    modelConfig: "/model-train/config",
    modelTrainInit: "/model-train/init",
    modelTrainModel: "/model-train/model",
    accuracy:"/model-train/:pk/accuracy",
  },
  alwaysExpectJSON: false,
};
