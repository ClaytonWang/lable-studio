import React, { useCallback, useContext, useEffect, useState } from "react";
import { Button } from "../../components";
import { Form, Input, Select, TextArea } from "../../components/Form";
import { RadioGroup } from "../../components/Form/Elements/RadioGroup/RadioGroup";
import { ProjectContext } from "../../providers/ProjectProvider";
import { Block } from "../../utils/bem";
import { useAPI } from "@/providers/ApiProvider";

export const GeneralSettings = () => {
  const { project, fetchProject } = useContext(ProjectContext);
  const [collections, setCollections] = useState([]);
  const api = useAPI();

  useEffect(() => {
    api
      .callApi("collections", {
        params: { page_size: 999 },
      })
      .then((res) => {
        setCollections([
          { id: "-1", title: t("project_without_collection", t("project_without_collection")) },
          ...res.results,
        ]);
      });
  }, []);

  const updateProject = useCallback(() => {
    if (project.id) fetchProject(project.id, true);
  }, [project]);

  const colors = [
    "#FFFFFF",
    "#F52B4F",
    "#FA8C16",
    "#F6C549",
    "#9ACA4F",
    "#51AAFD",
    "#7F64FF",
    "#D55C9D",
  ];

  const samplings = [
    {
      value: "Sequential",
      label: t("Sequential"),
      description: t("sequential_desc"),
    },
    { value: "Uniform", label: t("Random"), description: t("random_desc") },
  ];

  return (
    <div style={{ width: 480 }}>
      <Form
        action="updateProject"
        formData={{ ...project }}
        params={{ pk: project.id }}
        onSubmit={updateProject}
      >
        <Form.Row columnCount={1} rowGap="32px">
          <Input
            name="title"
            label={t("Project Name")}
            labelProps={{ large: true }}
          />

          <TextArea
            name="description"
            label={t("Description")}
            labelProps={{ large: true }}
            style={{ minHeight: 128 }}
          />

          <Select
            name="set_id"
            label={t("choose_project_collection")}
            labelProps={{ large: true }}
            options={collections.map((item) => ({
              label: item.title,
              value: item.id,
            }))}
          />

          <RadioGroup
            name="color"
            label={t("Color")}
            size="large"
            labelProps={{ size: "large" }}
          >
            {colors.map((color) => (
              <RadioGroup.Button key={color} value={color}>
                <Block name="color" style={{ "--background": color }} />
              </RadioGroup.Button>
            ))}
          </RadioGroup>

          <RadioGroup
            label={t("Task Sampling")}
            labelProps={{ size: "large" }}
            name="sampling"
            simple
          >
            {samplings.map(({ value, label, description }) => (
              <RadioGroup.Button
                key={value}
                value={`${value} sampling`}
                label={label}
                description={description}
              />
            ))}
          </RadioGroup>
        </Form.Row>

        <Form.Actions>
          <Form.Indicator>
            <span case="success">{t("Saved!", "已保存")}</span>
          </Form.Indicator>
          <Button type="submit" look="primary" style={{ width: 120 }}>
            {t("Save")}
          </Button>
        </Form.Actions>
      </Form>
    </div>
  );
};

GeneralSettings.menuItem = t("General");
GeneralSettings.path = "/";
GeneralSettings.exact = true;
