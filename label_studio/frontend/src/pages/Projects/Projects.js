import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useParams as useRouterParams } from "react-router";
import { Redirect } from "react-router-dom";
import { Select } from "../../components/Form";
import { Button } from "../../components";
import { Oneof } from "../../components/Oneof/Oneof";
import { Loading } from "../../components";
import { Space } from "@/components/Space/Space";
import { ApiContext } from "../../providers/ApiProvider";
import { useContextProps } from "../../providers/RoutesProvider";
import { Block, Elem } from "../../utils/bem";
import { CreateProject } from "../CreateProject/CreateProject";
import { DataManagerPage } from "../DataManager/DataManager";
import { SettingsPage } from "../Settings";
import "./Projects.styl";
import { EmptyProjectsList, ProjectsList } from "./ProjectsList";
import { useConfig } from "@/providers/ConfigProvider";

const getCurrentPage = () => {
  const pageNumberFromURL = new URLSearchParams(location.search).get("page");

  return pageNumberFromURL ? parseInt(pageNumberFromURL) : 1;
};

export const ProjectsPage = () => {
  const api = React.useContext(ApiContext);
  const config = useConfig();
  const [projectsList, setProjectsList] = React.useState([]);
  const [networkState, setNetworkState] = React.useState(null);
  const [currentPage, setCurrentPage] = useState(getCurrentPage());
  const [collections, setCollections] = useState([]);
  const [collection, setCollection] = useState("__all__");
  const [totalItems, setTotalItems] = useState(1);
  const setContextProps = useContextProps();
  const defaultPageSize = parseInt(
    localStorage.getItem("pages:projects-list") ?? 10,
  );
  const history = useHistory();

  const [modal, setModal] = React.useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);

  const gotoCollection = () => {
    history.push("/collections");
  };

  const fetchProjects = useCallback(async (
    page = currentPage,
    pageSize = defaultPageSize,
  ) => {
    setNetworkState("loading");
    const data = await api.callApi("projects", {
      params: {
        page,
        page_size: pageSize,
        ...(collection === '__all__' ? {} : { set_id: collection }),
      },
    });

    setTotalItems(data?.count ?? 1);
    setProjectsList(data.results ?? []);
    setNetworkState("loaded");
  }, [collection]);

  useMemo(() => {
    fetchProjects(currentPage);
  }, [collection, currentPage]);

  const loadNextPage = async (page) => {
    setCurrentPage(page);
  };

  React.useEffect(() => {
    api
      .callApi("collections", {
        params: { page_size: 999 },
      })
      .then((res) => {
        setCollections([
          { id: "__all__", title: t("all_project", "全部项目") },
          { id: "-1", title: t("project_without_collection", "无集合项目") },
          ...res.results,
        ]);
      });
  }, []);

  React.useEffect(() => {
    // there is a nice page with Create button when list is empty
    // so don't show the context button in that case
    setContextProps({
      openModal,
      showButton: projectsList.length > 0,
      gotoCollection,
      config,
    });
  }, [projectsList.length]);

  return (
    <Block name="projects-page">
      <Elem name="collection">
        <Space>
          <Elem name="title">{t("collection", "项目集合")}</Elem>
          <Elem name="select">
            <Select
              value={collection}
              onChange={(e) => setCollection(e.target.value)}
              options={collections.map((item) => ({
                label: item.title,
                value: item.id,
              }))}
            />
          </Elem>
        </Space>
      </Elem>
      <Oneof value={networkState}>
        <Elem name="loading" case="loading">
          <Loading size={64} />
        </Elem>
        <Elem name="content" case="loaded">
          <>
            {projectsList.length ? (
              <ProjectsList
                projects={projectsList}
                currentPage={currentPage}
                totalItems={totalItems}
                loadNextPage={loadNextPage}
                pageSize={defaultPageSize}
                fetchProjects={fetchProjects}
              />
            ) : (
              <EmptyProjectsList openModal={openModal} />
            )}
          </>
          {modal && <CreateProject onClose={closeModal} />}
        </Elem>
      </Oneof>
    </Block>
  );
};

ProjectsPage.title = t("Projects");
ProjectsPage.path = "/projects";
ProjectsPage.exact = true;
ProjectsPage.routes = ({ store }) => [
  {
    title: () =>
      store.project?.bread_crumbs_title
        ? store.project?.bread_crumbs_title
        : store.project?.title,
    bread_crumbs_title: () => store.project?.bread_crumbs_title,
    path: "/:id(\\d+)",
    exact: true,
    component: () => {
      const params = useRouterParams();

      return <Redirect to={`/projects/${params.id}/data`} />;
    },
    pages: {
      DataManagerPage,
      SettingsPage,
    },
  },
];
ProjectsPage.context = ({ openModal, showButton, gotoCollection,config }) => {
  if (!showButton) return null;
  return (
    <Space>
      {
        !Object.keys(config.user.button).includes("004")&&(
          <Button onClick={gotoCollection} look="primary" size="compact">
            {t("Project collection", "项目集合设置")}
          </Button>
        )
      }
      <Button onClick={openModal} look="primary" size="compact">
        {t("Insert", "新增")}
      </Button>
    </Space>
  );
};
