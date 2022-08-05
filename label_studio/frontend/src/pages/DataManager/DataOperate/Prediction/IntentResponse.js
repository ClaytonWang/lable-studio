import React, { useCallback,useEffect ,useState } from 'react';
import { Col,Form,Row ,Tag } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { Select } from '@/components/Form';
import { useProject } from '@/providers/ProjectProvider';
import { ConfigureControl } from '@/pages/CreateProject/Config/Config';
import { Template } from '@/pages/CreateProject/Config/Template';
import { useAPI } from '@/providers/ApiProvider';

const { confirm } = Modal;

const formItemLayout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

const IntentResponse = ({ close, execLabel }) => {
  const { project } = useProject();
  const [template, setCurrentTemplate] = useState(null);
  const [config, _setConfig] = React.useState("");
  const api = useAPI();

  const setConfig = useCallback(config => {
    _setConfig(config);
  }, [_setConfig]);

  const setTemplate = useCallback(config => {
    const tpl = new Template({ config });

    tpl.onConfigUpdate = setConfig;
    setConfig(config);
    setCurrentTemplate(tpl);
  }, [setConfig, setCurrentTemplate]);

  useEffect(() => {
    if (project.label_config) {
      setTemplate(project.label_config);
    }
  }, []);

  const saveConfig = useCallback(async () => {
    const res = await api.callApi("updateProjectRaw", {
      params: {
        pk: project.id,
      },
      body: {
        label_config: config,
      },
    });

    if (res.ok) {
      execLabel();
      close();
      return true;
    }

    const error = await res.json();

    return error;
  }, [project, config]);

  const exec = () => {
    const changedLabels = [];
    const labels =[];

    template.controls.map(ctl => {
      changedLabels.push(Array.from(ctl.children).map(c => {
        return c.getAttribute("value");
      }));
    });

    //判断新旧标签是否相同
    const isSame = labels.length === changedLabels.length && labels.filter(t => !changedLabels.includes(t));

    if (!isSame) {
      confirm({
        title: "警告",
        body: "模型标签和已设置标签不一致是否继续标注?",
        buttonLook: "destructive",
        onOk: () => {
          //go exec
          saveConfig();
        },
        okText: "继续标注",
        cancelText: "返回修改",
      });
    } else {
      //go exec
      saveConfig();
    }
  };

  return (
    <>
      <Modal.Header>
      预标注(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
        layout="horizontal"
        name="form_in_modal"
        className='modal_form'
      >
        <Form.Item
          label="选择模型"
        >
          <div style={{ width: 300 }}>
            <Select
              options={[
                { label: '请选择模型名称', value: '' },
                { label: '对话意图', value: 'intention' },
                { label: '对话生成', value: 'generation' },
                { label: '清洗模型', value: 'clean' },
                { label: '其他', value: 'other' },
              ]}
              placeholder={t("Please select Model type")} />
          </div>
        </Form.Item>
        <Form.Item
          label="所选模型标签"
        >
          <Space size="small">
            <Tag>升级</Tag>
            <Tag>不知情</Tag>
            <Tag>套餐</Tag>
          </Space>
          <div style={{ color: 'red',marginTop:10 }}>注:所选模型标签和以设置标签</div>
        </Form.Item>
      </Form>
      {template && template.controls.map(control => {
        return (
          <Row key={control.getAttribute("name")} className={'configure-row'}>
            <Col span={5} className={ 'ant-form-item-label'}>
              <label>已设置标签</label>
            </Col>
            <Col span={19} >
              <ConfigureControl control={control} template={template} />
            </Col>
          </Row>
        );
      })}
      <Modal.Footer>
        <Space align="end">
          <Button
            size="compact"
            onClick={close}
          >
            取消
          </Button>
          <Button
            size="compact"
            look="primary"
            onClick={ exec}
          >
            立即标注
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default IntentResponse;
