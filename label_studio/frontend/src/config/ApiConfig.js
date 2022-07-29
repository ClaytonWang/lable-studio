export const API_CONFIG = {
  gateway: `${window.APP_SETTINGS.hostname}/api`,
  // gateway: `http://124.71.161.146:8080/api`,
  endpoints: {
    // Users
    users: "/users",
    me: "/current-user/whoami",

    // Organization
    memberships: "/organizations/:pk/memberships",
    inviteLink: "/invite",
    resetInviteLink: "POST:/invite/reset-token",
    orgList: "GET:/organizations",
    addOrg: "POST:/organizations",
    updateOrg: "PATCH:/organizations/:pk",
    deleteOrg: "DELETE:/organizations/:pk",
    orgDetail: "GET:/organizations/:pk",
    changeOrg: "PATCH:/organizations/change",

    // Project
    projects: "/projects",
    project: "/projects/:pk",
    updateProject: "PATCH:/projects/:pk",
    createProject: "POST:/projects",
    deleteProject: "DELETE:/projects/:pk",

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
    exportModel: "GET:/model-manager/export",
    filtersModel: "GET:/model-manager/select",

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

    // Prompt Learning
    mlPromptPredict: 'POST:/projects/prompt-learning/predict',
    mlPromptTemplateCreate: 'POST:/templates/prompt-learning',
    mlPromptTemplateDelete: 'DELETE:/templates/prompt-learning',
    mlPromptTemplateUpdate: 'PATCH:/templates/prompt-learning',
    mlPromptTemplateQuery: 'GET:/templates/prompt-learning/:project',

    // Clean
    clExec: "POST:/dbml/clean",
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
  },
  alwaysExpectJSON: false,
};
