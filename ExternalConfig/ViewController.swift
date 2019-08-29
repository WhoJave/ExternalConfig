//
//  ViewController.swift
//  ExternalConfig
//
//  Created by asd on 6/8/2019.
//  Copyright © 2019 OnePiece. All rights reserved.
//

import Cocoa

class ViewController: NSViewController,NSUserNotificationCenterDelegate {

    @IBOutlet weak var portNum: NSTextField!
    @IBOutlet weak var subType: NSComboBox!
    @IBOutlet weak var subScribeURL: NSTextField!
    @IBOutlet var resutView: NSTextView!
    @IBOutlet weak var execButton: NSButton!
    @IBAction func runSSR2JSON(_ sender: NSButton) {
        subScribeURL.resignFirstResponder()
        resutView.string = "处理中请稍后..."
        execButton.isEnabled = false
        runScript()
    }
    
    @IBAction func copy(_ sender: NSButton) {
        let pasteBoard = NSPasteboard.general
        pasteBoard.declareTypes([NSPasteboard.PasteboardType.init("NSStringPboardType")], owner: nil)
        if resutView.string.count == 0 {
            //没有可复制的内容
            print("没有可复制的内容")
        }else{
            let copySuccess = pasteBoard.setString(resutView.string, forType: NSPasteboard.PasteboardType.init("NSStringPboardType"))
            if copySuccess {
                showNotification(content: "")
            }
        }
        
        
    }
    
    func showNotification(content: String){
        let notice = NSUserNotification.init()
        notice.title = "复制External配置到剪切板"
        notice.subtitle = "复制成功"
        
        let center = NSUserNotificationCenter.default
        center.delegate = self
        center.scheduleNotification(notice)
    }
    
    func userNotificationCenter(_ center: NSUserNotificationCenter, shouldPresent notification: NSUserNotification) -> Bool {
        return true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        resutView.isEditable = false
        // Do any additional setup after loading the view.
    }

    func runScript() {
        guard let aPath = Bundle.main.path(forResource: "RSS", ofType: "py") else { return }
        
        let script = CocoaPython(scrPath: aPath, args: fetchArgs()) { [weak self] in
            self?.scriptFinish(results: $0, error: $1)
        }
        
        script.runAsync()
    }
    
    func fetchArgs() -> [String] {
        let args = ["-s \(subScribeURL.stringValue)"]
        return args
    }
    
    // 执行完成的回调
    func scriptFinish(results: [String], error: String?) {
        if let aError = error {
            resutView.string = "解析错误\r\n" + aError
            execButton.isEnabled = true
            return
        }
        resutView.string = results[0]
        execButton.isEnabled = true
    }
    
    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

