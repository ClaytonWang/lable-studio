import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState
} from "react";
import chr from "chroma-js";
import { format } from "date-fns";
import { NavLink } from "react-router-dom";
import { LsBulb, LsCheck, LsEllipsis, LsMinus } from "../../assets/icons";
import { Dropdown, Form, Input,Menu,Select } from "antd";
import { Button, Pagination, Userpic } from "../../components";
import { Space } from "@/components/Space/Space";
import { Modal } from "@/components/Modal/Modal";
import { useAPI } from "@/providers/ApiProvider";
import { Block, Elem } from "../../utils/bem";
import "./ProjectList.less";

export const ProjectsList = ({
  projects,
  currentPage,
  totalItems,
  loadNextPage,
  pageSize,
  fetchProjects,
}) => {
  const modalRef = useRef();
  const [collections, setCollections] = useState([]);
  const [current, setCurrent] = useState();
  const api = useAPI();
  const [form] = Form.useForm();

  useEffect(() => {
    api
      .callApi("collections", {
        params: { page_size: 999 },
      })
      .then((res) => {
        setCollections([
          {
            id: "-1",
            title: t(
              "project_without_collection",
              t("project_without_collection"),
            ),
          },
          ...res.results,
        ]);
      });
  }, []);

  useEffect(() => {
    if (current) {
      modalRef.current?.show();
    } else if (current === null) {
      modalRef.current?.hide();
    }
  }, [current]);
  const onFinish = useCallback(() => {
    form.validateFields().then((values) => {
      api.callApi('updateProject', {
        params: { pk: current.id },
        body: values,
      }).then(() => {
        fetchProjects();
      });
    });
  }, [form, current, fetchProjects, setCurrent]);

  return (
    <>
      <Elem name="list">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
          />
        ))}
      </Elem>
      <Elem name="pages">
        <Pagination
          name="projects-list"
          label={t("Projects")}
          page={currentPage}
          totalItems={totalItems}
          urlParamName="page"
          pageSize={pageSize}
          pageSizeOptions={[10, 30, 50, 100]}
          onPageLoad={(page, pageSize) => loadNextPage(page, pageSize)}
        />
      </Elem>
      <Modal
        bare
        ref={modalRef}
        style={{ width: 400 }}
        allowClose={false}
        className="project-collection"
      >
        <Modal.Header>{t("change_collection", "变更集合")}</Modal.Header>
        <Form form={form} labelCol={{ span: 8 }} wrapperCol={{ span: 12 }}>
          <Form.Item label={t("current_collection", "当前集合")}>
            <Input
              disabled
              value={current?.set_title || t("project_without_collection")}
            />
          </Form.Item>
          <Form.Item
            name="set_id"
            label={t("changed_collection", "变更后集合")}
            rules={[
              {
                required: true,
                message: t("placeholder_select_collection", "请选择集合"),
              },
            ]}
          >
            <Select
              placeholder={t("placeholder_select_collection", "请选择集合")}
            >
              {collections.map((item) => {
                return (
                  <Select.Option key={item.id} value={item.id}>
                    {item.title}
                  </Select.Option>
                );
              })}
            </Select>
          </Form.Item>
        </Form>
        <Modal.Footer>
          <Space align="end">
            <Button size="compact" onClick={() => setCurrent(null)}>
              {t("Cancel")}
            </Button>
            <Button size="compact" look="primary" onClick={onFinish}>
              {t("Confirm")}
            </Button>
          </Space>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export const EmptyProjectsList = ({ openModal }) => {
  return (
    <Block name="empty-projects-page">
      {/* <Elem name="heidi" tag="img" src={absoluteURL("/static/images/opossum_looking.png")} /> */}
      <Elem name="header" tag="h1">
        {t("Nothing found")}
      </Elem>
      <p>{t("Go to import")}</p>
      <Elem name="action" tag={Button} onClick={openModal} look="primary">
        {t("Create Project")}
      </Elem>
    </Block>
  );
};

const ProjectCard = ({ project }) => {

  const color = useMemo(() => {
    return project.color === "#FFFFFF" ? null : project.color;
  }, [project]);

  const projectColors = useMemo(() => {
    return color
      ? {
        "--header-color": color,
        "--background-color": chr(color).alpha(0.2).css(),
      }
      : {};
  }, [color]);

  const menu = (
    <Menu
      items={[
        {
          label: (
            <Elem
              tag={NavLink}
              name="link"
              data-external
              to={`/projects/${project.id}/settings`}>
              { t("Settings")}
            </Elem>),
          key: '1',
        },
        {
          label: (
            <Elem
              tag={NavLink}
              name="link"
              data-external
              to={`/projects/${project.id}/data?labeling=1`}>
              { t("Labels")}
            </Elem>),
          key: '2',
        },
      ]}
    />
  );

  return (
    <Elem
      tag={NavLink}
      name="link"
      to={`/projects/${project.id}/data`}
      data-external
    >
      <Block
        name="project-card"
        mod={{ colored: !!color }}
        style={projectColors}
      >
        <Elem name="header">
          <Elem name="title">
            <Elem name="title-text">{project.title ?? t("New Project")}</Elem>

            <Elem
              name="menu"
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
              }}
            >
              <Dropdown
                trigger={['click']}
                overlay={(menu)}
              >
                <Button size="small" type="text" icon={<LsEllipsis />} />
              </Dropdown>
            </Elem>
          </Elem>
          <Elem name="summary">
            <Elem name="annotation">
              <Elem name="total">
                {project.num_tasks_with_annotations} / {project.task_number}
              </Elem>
              <Elem name="detail">
                <Elem name="detail-item" mod={{ type: "completed" }}>
                  <Elem tag={LsCheck} name="icon" />
                  {project.total_annotations_number}
                </Elem>
                <Elem name="detail-item" mod={{ type: "rejected" }}>
                  <Elem tag={LsMinus} name="icon" />
                  {project.skipped_annotations_number}
                </Elem>
                <Elem name="detail-item" mod={{ type: "predictions" }}>
                  <Elem tag={LsBulb} name="icon" />
                  {project.total_predictions_number}
                </Elem>
              </Elem>
            </Elem>
          </Elem>
        </Elem>
        <Elem name="description">{project.description}</Elem>
        <Elem name="info">
          <Elem name="created-date">
            {format(new Date(project.created_at), "yy-MM-dd HH:mm")}
          </Elem>
          <Elem name="created-by">
            <Userpic src="#" user={project.created_by} showUsername />
          </Elem>
        </Elem>
      </Block>
    </Elem>
  );
};
